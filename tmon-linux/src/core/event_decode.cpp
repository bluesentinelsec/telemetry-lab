#include "core/event_decode.hpp"

#include <cstring>

#include "bpf/tmon_event.h"

namespace tmon {

Event DecodeEvent(const ::tmon_event& w) {
  Event e;
  switch (w.kind) {
    case TMON_FORK: e.kind = EventKind::kFork; break;
    case TMON_EXEC: e.kind = EventKind::kExec; break;
    case TMON_EXIT: e.kind = EventKind::kExit; break;
    case TMON_SYSCALL:
    default: e.kind = EventKind::kSyscall; break;
  }
  e.ts_ns = w.ts_ns;
  e.pid = w.pid;
  e.tid = w.tid;
  e.child_pid = w.child_pid;
  e.syscall_nr = w.syscall_nr;
  e.exit_code = w.exit_code;
  for (int i = 0; i < kSyscallArgs; i++) e.args[i] = w.args[i];
  // comm is a fixed-size, not-necessarily-terminated field; bound the copy.
  e.comm.assign(w.comm, ::strnlen(w.comm, TMON_COMM_LEN));
  return e;
}

}  // namespace tmon
