#include <catch2/catch_test_macros.hpp>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#include <cstring>

#include "bpf/tmon_event.h"
#include "core/event_decode.hpp"
#include "model/event.hpp"

using namespace tmon;

TEST_CASE("a SYS_ENTER decodes args and a path argument", "[decode]") {
  tmon_event w{};
  w.kind = TMON_SYS_ENTER;
  w.ts_ns = 123456;
  w.pid = 10;
  w.tid = 11;
  w.syscall_nr = 257;  // openat
  for (int i = 0; i < TMON_SYSCALL_ARGS; i++) w.args[i] = 0x100ULL + i;
  std::strcpy(w.comm, "cat");
  std::strcpy(w.str, "/etc/hostname");
  w.str_len = static_cast<unsigned>(std::strlen("/etc/hostname") + 1);
  w.str_argno = 1;

  Event e = DecodeEvent(w);
  REQUIRE(e.kind == EventKind::kSyscall);
  REQUIRE(e.syscall_nr == 257);
  REQUIRE(e.pid == 10);
  REQUIRE(e.comm == "cat");
  REQUIRE(e.args[5] == 0x105ULL);
  REQUIRE(e.path == "/etc/hostname");
  REQUIRE(e.path_argno == 1);
  REQUIRE_FALSE(e.has_ret);
}

TEST_CASE("a SYS_EXIT decodes the return value and errno", "[decode]") {
  tmon_event w{};
  w.kind = TMON_SYS_EXIT;
  w.syscall_nr = 257;

  SECTION("success") {
    w.ret = 3;
    Event e = DecodeEvent(w);
    REQUIRE(e.has_ret);
    REQUIRE(e.ret == 3);
    REQUIRE(e.error == 0);
  }
  SECTION("failure maps -errno to errno") {
    w.ret = -2;  // -ENOENT
    Event e = DecodeEvent(w);
    REQUIRE(e.has_ret);
    REQUIRE(e.ret == -2);
    REQUIRE(e.error == 2);
  }
  SECTION("large non-error return is not mistaken for errno") {
    w.ret = 0x7fffffffffffLL;  // e.g. an mmap address, well outside [-4095,-1]
    Event e = DecodeEvent(w);
    REQUIRE(e.error == 0);
  }
}

TEST_CASE("fork/exec/exit kinds and their payloads map", "[decode]") {
  tmon_event w{};

  w.kind = TMON_FORK;
  w.child_pid = 42;
  REQUIRE(DecodeEvent(w).kind == EventKind::kFork);
  REQUIRE(DecodeEvent(w).child_pid == 42);

  w.kind = TMON_EXEC;
  REQUIRE(DecodeEvent(w).kind == EventKind::kExec);

  w.kind = TMON_EXIT;
  w.exit_code = 7;
  Event e = DecodeEvent(w);
  REQUIRE(e.kind == EventKind::kExit);
  REQUIRE(e.exit_code == 7);
}

TEST_CASE("comm is bounded when the kernel field has no terminator",
          "[decode]") {
  tmon_event w{};
  w.kind = TMON_SYS_ENTER;
  std::memset(w.comm, 'A', TMON_COMM_LEN);  // deliberately not NUL-terminated
  Event e = DecodeEvent(w);
  REQUIRE(e.comm.size() == TMON_COMM_LEN);
}

TEST_CASE("DecodeSockaddr renders IPv4 and IPv6 and degrades gracefully",
          "[decode][sockaddr]") {
  SECTION("AF_INET -> ip:port") {
    sockaddr_in sa{};
    sa.sin_family = AF_INET;
    sa.sin_port = htons(9999);
    inet_pton(AF_INET, "127.0.0.1", &sa.sin_addr);
    unsigned char buf[TMON_SADDR_LEN] = {0};
    std::memcpy(buf, &sa, sizeof(sa));
    REQUIRE(DecodeSockaddr(buf, sizeof(buf)) == "127.0.0.1:9999");
  }
  SECTION("AF_INET6 -> [ip]:port") {
    sockaddr_in6 sa{};
    sa.sin6_family = AF_INET6;
    sa.sin6_port = htons(443);
    inet_pton(AF_INET6, "::1", &sa.sin6_addr);
    unsigned char buf[TMON_SADDR_LEN] = {0};
    std::memcpy(buf, &sa, sizeof(sa));
    REQUIRE(DecodeSockaddr(buf, sizeof(buf)) == "[::1]:443");
  }
  SECTION("too few bytes -> empty") {
    unsigned char buf[1] = {0};
    REQUIRE(DecodeSockaddr(buf, 1).empty());
  }
}
