#include "view/human_formatter.hpp"

#include <cstdio>

#include "core/syscall_names.hpp"

namespace tmon {

double HumanFormatter::RelativeSeconds(std::uint64_t ts_ns) {
  if (!have_first_ts_) {
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
      out_ << '(';
      for (int i = 0; i < kSyscallArgs; i++) {
        if (i) out_ << ", ";
        char buf[20];
        std::snprintf(buf, sizeof(buf), "0x%llx",
                      static_cast<unsigned long long>(event.args[i]));
        out_ << buf;
      }
      out_ << ")\n";
      break;
    }
    case EventKind::kFork:
      out_ << "+++ fork -> child " << event.child_pid << " +++\n";
      break;
    case EventKind::kExec:
      out_ << "+++ exec (now " << event.comm << ") +++\n";
      break;
    case EventKind::kExit:
      out_ << "+++ exited with " << event.exit_code << " +++\n";
      break;
  }
}

void HumanFormatter::End(const Summary& summary) {
  if (config_.quiet) return;
  out_ << "tmon: " << summary.syscall_events << " syscalls, "
       << summary.total_events << " events, " << summary.processes
       << " process(es); target exit " << summary.target_exit_code << "\n";
}

}  // namespace tmon
