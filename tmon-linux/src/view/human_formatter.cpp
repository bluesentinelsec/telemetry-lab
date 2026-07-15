#include "view/human_formatter.hpp"

#include <cinttypes>
#include <cstdio>

#include "core/errno_names.hpp"
#include "core/syscall_names.hpp"

namespace tmon {

double HumanFormatter::RelativeSeconds(std::uint64_t ts_ns) {
  // Rebase to the earliest timestamp seen. Paired syscalls carry their enter
  // time, which can precede an already-emitted fork/exec marker, so the first
  // event is not always the earliest; tracking the minimum avoids underflow.
  if (!have_first_ts_ || ts_ns < first_ts_ns_) {
    first_ts_ns_ = ts_ns;
    have_first_ts_ = true;
  }
  return static_cast<double>(ts_ns - first_ts_ns_) / 1e9;
}

void HumanFormatter::Begin() {
  if (config_.summary_only) return;
  out_ << "tmon: tracing '" << config_.command.front() << "'\n";
}

void HumanFormatter::Handle(const Event& event) {
  if (config_.summary_only) return;

  char prefix[64];
  std::snprintf(prefix, sizeof(prefix), "%11.6f %-6u %-16s ",
                RelativeSeconds(event.ts_ns), event.pid, event.comm.c_str());
  out_ << prefix;

  switch (event.kind) {
    case EventKind::kSyscall: {
      const char* name = SyscallName(event.syscall_nr);
      if (name)
        out_ << name;
      else
        out_ << "syscall_" << event.syscall_nr;

      // Arguments: substitute the decoded path/sockaddr at their index, hex else.
      out_ << '(';
      for (int i = 0; i < kSyscallArgs; i++) {
        if (i) out_ << ", ";
        if (i == event.path_argno && !event.path.empty()) {
          out_ << '"' << event.path << '"';
        } else if (i == event.sockaddr_argno && !event.sockaddr.empty()) {
          out_ << event.sockaddr;
        } else {
          char buf[20];
          std::snprintf(buf, sizeof(buf), "0x%llx",
                        static_cast<unsigned long long>(event.args[i]));
          out_ << buf;
        }
      }
      out_ << ')';

      // Result: " = <ret>" and the errno symbol on failure.
      if (event.has_ret) {
        out_ << " = " << event.ret;
        if (event.error != 0) {
          const char* en = ErrnoName(event.error);
          out_ << ' ' << (en ? en : "errno") << '(' << event.error << ')';
        }
      }
      // Duration, strace -T style.
      if (event.has_duration) {
        char dbuf[32];
        std::snprintf(dbuf, sizeof(dbuf), " <%.6f>",
                      static_cast<double>(event.duration_ns) / 1e9);
        out_ << dbuf;
      }
      out_ << '\n';
      break;
    }
    case EventKind::kFork:
      out_ << "+++ fork -> child " << event.child_pid << " +++\n";
      break;
    case EventKind::kExec:
      out_ << "+++ exec ";
      if (!event.path.empty()) out_ << '"' << event.path << "\" ";
      out_ << "(now " << event.comm << ") +++\n";
      break;
    case EventKind::kExit:
      out_ << "+++ exited with " << event.exit_code << " +++\n";
      break;
  }
}

void HumanFormatter::End(const Summary& summary) {
  if (config_.quiet) return;
  out_ << "tmon: " << summary.syscall_events << " syscalls ("
       << summary.failed_syscalls << " failed), " << summary.total_events
       << " events, " << summary.processes << " process(es), "
       << summary.dropped << " dropped; target exit "
       << summary.target_exit_code << "\n";
}

}  // namespace tmon
