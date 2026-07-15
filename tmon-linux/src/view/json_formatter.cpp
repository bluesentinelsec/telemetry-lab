#include "view/json_formatter.hpp"

#include <cJSON.h>

#include <cstdio>
#include <memory>

#include "core/syscall_names.hpp"

namespace tmon {
namespace {

// RAII for a cJSON tree we own and must free.
struct CjsonDeleter {
  void operator()(cJSON* p) const { cJSON_Delete(p); }
};
using CjsonPtr = std::unique_ptr<cJSON, CjsonDeleter>;

// Serialize `obj` compactly and write it as one line. Consumes nothing; caller
// still owns `obj`.
void PrintLine(std::ostream& out, cJSON* obj) {
  char* text = cJSON_PrintUnformatted(obj);
  if (text) {
    out << text << '\n';
    cJSON_free(text);
  }
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
  cJSON_AddNumberToObject(root.get(), "ts_ns",
                          static_cast<double>(event.ts_ns));
  cJSON_AddNumberToObject(root.get(), "pid", event.pid);
  cJSON_AddNumberToObject(root.get(), "tid", event.tid);
  cJSON_AddStringToObject(root.get(), "comm", event.comm.c_str());

  switch (event.kind) {
    case EventKind::kSyscall: {
      cJSON_AddNumberToObject(root.get(), "nr",
                              static_cast<double>(event.syscall_nr));
      const char* name = SyscallName(event.syscall_nr);
      if (name) cJSON_AddStringToObject(root.get(), "syscall", name);
      cJSON* args = cJSON_AddArrayToObject(root.get(), "args");
      for (int i = 0; i < kSyscallArgs; i++) {
        // Emit as hex strings so full 64-bit values survive JSON's double.
        char buf[20];
        std::snprintf(buf, sizeof(buf), "0x%llx",
                      static_cast<unsigned long long>(event.args[i]));
        cJSON_AddItemToArray(args, cJSON_CreateString(buf));
      }
      break;
    }
    case EventKind::kFork:
      cJSON_AddNumberToObject(root.get(), "child_pid", event.child_pid);
      break;
    case EventKind::kExit:
      cJSON_AddNumberToObject(root.get(), "exit_code", event.exit_code);
      break;
    case EventKind::kExec:
      break;
  }
  PrintLine(out_, root.get());
}

void JsonFormatter::End(const Summary& summary) {
  CjsonPtr root(cJSON_CreateObject());
  cJSON_AddStringToObject(root.get(), "record", "summary");
  cJSON_AddNumberToObject(root.get(), "syscall_events",
                          static_cast<double>(summary.syscall_events));
  cJSON_AddNumberToObject(root.get(), "total_events",
                          static_cast<double>(summary.total_events));
  cJSON_AddNumberToObject(root.get(), "processes", summary.processes);
  cJSON_AddNumberToObject(root.get(), "target_exit_code",
                          summary.target_exit_code);
  PrintLine(out_, root.get());
}

}  // namespace tmon
