#include "view/json_formatter.hpp"

#include <cJSON.h>

#include <cstdio>
#include <memory>

#include "core/errno_names.hpp"
#include "core/syscall_names.hpp"

namespace tmon {
namespace {

struct CjsonDeleter {
  void operator()(cJSON* p) const { cJSON_Delete(p); }
};
using CjsonPtr = std::unique_ptr<cJSON, CjsonDeleter>;

void PrintLine(std::ostream& out, cJSON* obj) {
  char* text = cJSON_PrintUnformatted(obj);
  if (text) {
    out << text << '\n';
    cJSON_free(text);
  }
}

// cJSON's number API converts through double, rounding 64-bit values and
// sometimes printing exponent notation. A decimal integer token is already
// valid JSON; serialize it directly without losing bits.
template <typename Integer>
void AddInteger(cJSON* obj, const char* key, Integer value) {
  const std::string decimal = std::to_string(value);
  cJSON_AddRawToObject(obj, key, decimal.c_str());
}

const char* KindName(EventKind kind) {
  switch (kind) {
    case EventKind::kSyscall: return "syscall";
    case EventKind::kFork: return "fork";
    case EventKind::kExec: return "exec";
    case EventKind::kExit: return "exit";
  }
  return "unknown";
}

}  // namespace

void JsonFormatter::Begin() {
  CjsonPtr root(cJSON_CreateObject());
  cJSON_AddStringToObject(root.get(), "record", "meta");
  cJSON_AddStringToObject(root.get(), "tool", "tmon");

  cJSON* cmd = cJSON_AddArrayToObject(root.get(), "command");
  for (const auto& s : config_.command)
    cJSON_AddItemToArray(cmd, cJSON_CreateString(s.c_str()));

  if (!config_.meta.empty()) {
    cJSON* meta = cJSON_AddObjectToObject(root.get(), "meta");
    for (const auto& kv : config_.meta)
      cJSON_AddStringToObject(meta, kv.first.c_str(), kv.second.c_str());
  }
  PrintLine(out_, root.get());
}

void JsonFormatter::Handle(const Event& event) {
  CjsonPtr root(cJSON_CreateObject());
  cJSON_AddStringToObject(root.get(), "record", "event");
  cJSON_AddStringToObject(root.get(), "kind", KindName(event.kind));
  AddInteger(root.get(), "ts_ns", event.ts_ns);
  cJSON_AddNumberToObject(root.get(), "pid", event.pid);
  cJSON_AddNumberToObject(root.get(), "tid", event.tid);
  cJSON_AddStringToObject(root.get(), "comm", event.comm.c_str());

  switch (event.kind) {
    case EventKind::kSyscall: {
      AddInteger(root.get(), "nr", event.syscall_nr);
      const char* name = SyscallName(event.syscall_nr);
      if (name) cJSON_AddStringToObject(root.get(), "syscall", name);

      // Only the syscall's real arity (the rest of the six captured registers
      // are stale). Raw hex strings so full 64-bit values survive JSON's double.
      int arity = SyscallArity(event.syscall_nr);
      int count = (arity >= 0 && arity <= kSyscallArgs) ? arity : kSyscallArgs;
      cJSON* args = cJSON_AddArrayToObject(root.get(), "args");
      for (int i = 0; i < count; i++) {
        char buf[20];
        std::snprintf(buf, sizeof(buf), "0x%llx",
                      static_cast<unsigned long long>(event.args[i]));
        cJSON_AddItemToArray(args, cJSON_CreateString(buf));
      }
      if (!event.path.empty()) {
        cJSON_AddStringToObject(root.get(), "path", event.path.c_str());
        cJSON_AddNumberToObject(root.get(), "path_argno", event.path_argno);
      }
      if (!event.sockaddr.empty()) {
        cJSON_AddStringToObject(root.get(), "sockaddr", event.sockaddr.c_str());
        cJSON_AddNumberToObject(root.get(), "sockaddr_argno",
                                event.sockaddr_argno);
      }
      if (event.has_ret) {
        AddInteger(root.get(), "ret", event.ret);
        cJSON_AddBoolToObject(root.get(), "ok", event.error == 0);
        if (event.error != 0) {
          const char* en = ErrnoName(event.error);
          if (en) cJSON_AddStringToObject(root.get(), "error", en);
          cJSON_AddNumberToObject(root.get(), "errno", event.error);
        }
      }
      if (event.has_duration)
        AddInteger(root.get(), "duration_ns", event.duration_ns);
      break;
    }
    case EventKind::kFork:
      cJSON_AddNumberToObject(root.get(), "child_pid", event.child_pid);
      break;
    case EventKind::kExit:
      cJSON_AddNumberToObject(root.get(), "exit_code", event.exit_code);
      break;
    case EventKind::kExec:
      if (!event.path.empty())
        cJSON_AddStringToObject(root.get(), "path", event.path.c_str());
      break;
  }
  PrintLine(out_, root.get());
}

void JsonFormatter::End(const Summary& summary) {
  CjsonPtr root(cJSON_CreateObject());
  cJSON_AddStringToObject(root.get(), "record", "summary");
  AddInteger(root.get(), "syscall_events", summary.syscall_events);
  AddInteger(root.get(), "failed_syscalls", summary.failed_syscalls);
  AddInteger(root.get(), "total_events", summary.total_events);
  cJSON_AddNumberToObject(root.get(), "processes", summary.processes);
  AddInteger(root.get(), "dropped", summary.dropped);
  cJSON_AddNumberToObject(root.get(), "target_exit_code",
                          summary.target_exit_code);
  PrintLine(out_, root.get());
}

}  // namespace tmon
