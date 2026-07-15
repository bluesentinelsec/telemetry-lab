#include "core/event_decode.hpp"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#include <cstdint>
#include <cstring>

#include "bpf/tmon_event.h"

namespace tmon {
namespace {

// errno-bearing return values sit in [-4095, -1]; anything else is a real value.
int ErrorFromRet(std::int64_t ret) {
  if (ret < 0 && ret >= -4095) return static_cast<int>(-ret);
  return 0;
}

// Copy any decoded path / sockaddr the kernel captured into the domain event.
void FillDecoded(Event& e, const ::tmon_event& w) {
  if (w.str_len > 0) {
    e.path.assign(w.str, ::strnlen(w.str, TMON_STR_LEN));
    e.path_argno = w.str_argno;
  }
  if (w.saddr_len > 0) {
    e.sockaddr = DecodeSockaddr(w.saddr, w.saddr_len);
    e.sockaddr_argno = w.saddr_argno;
  }
}

}  // namespace

std::string DecodeSockaddr(const unsigned char* bytes, std::size_t len) {
  if (len < sizeof(std::uint16_t)) return "";
  std::uint16_t family;
  std::memcpy(&family, bytes, sizeof(family));  // sa_family is host-endian

  if (family == AF_INET && len >= sizeof(sockaddr_in)) {
    sockaddr_in sa{};
    std::memcpy(&sa, bytes, sizeof(sa));
    char ip[INET_ADDRSTRLEN] = {0};
    inet_ntop(AF_INET, &sa.sin_addr, ip, sizeof(ip));
    return std::string(ip) + ":" + std::to_string(ntohs(sa.sin_port));
  }
  if (family == AF_INET6 && len >= sizeof(sockaddr_in6)) {
    sockaddr_in6 sa{};
    std::memcpy(&sa, bytes, sizeof(sa));
    char ip[INET6_ADDRSTRLEN] = {0};
    inet_ntop(AF_INET6, &sa.sin6_addr, ip, sizeof(ip));
    return "[" + std::string(ip) + "]:" + std::to_string(ntohs(sa.sin6_port));
  }
  if (family == AF_UNIX && len > sizeof(std::uint16_t)) {
    const char* path = reinterpret_cast<const char*>(bytes + sizeof(std::uint16_t));
    std::size_t maxp = len - sizeof(std::uint16_t);
    return "unix:" + std::string(path, ::strnlen(path, maxp));
  }
  return "family=" + std::to_string(family);
}

Event DecodeEvent(const ::tmon_event& w) {
  Event e;
  e.ts_ns = w.ts_ns;
  e.pid = w.pid;
  e.tid = w.tid;
  e.comm.assign(w.comm, ::strnlen(w.comm, TMON_COMM_LEN));

  switch (w.kind) {
    case TMON_FORK:
      e.kind = EventKind::kFork;
      e.child_pid = w.child_pid;
      return e;
    case TMON_EXEC:
      e.kind = EventKind::kExec;
      // The exec path travels in str (from the tracepoint's filename field).
      if (w.str_len > 0) e.path.assign(w.str, ::strnlen(w.str, TMON_STR_LEN));
      return e;
    case TMON_EXIT:
      e.kind = EventKind::kExit;
      e.exit_code = w.exit_code;
      return e;
    case TMON_SYS_EXIT:
      e.kind = EventKind::kSyscall;
      e.syscall_nr = w.syscall_nr;
      e.has_ret = true;
      e.ret = w.ret;
      e.error = ErrorFromRet(w.ret);
      FillDecoded(e, w);  // paths/sockaddrs are decoded at exit
      return e;
    case TMON_SYS_ENTER:
    default:
      break;
  }

  // SYS_ENTER: args, plus any best-effort decode (only in --no-returns mode).
  e.kind = EventKind::kSyscall;
  e.syscall_nr = w.syscall_nr;
  for (int i = 0; i < kSyscallArgs; i++) e.args[i] = w.args[i];
  FillDecoded(e, w);
  return e;
}

}  // namespace tmon
