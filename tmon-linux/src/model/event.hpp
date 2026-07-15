// Layer 1 — data model. Pure domain types with no behavior beyond construction.
// The engine (layer 2) produces these; formatters (layer 3) consume them. This
// layer knows nothing about BPF, CLI11, or output formats.
#ifndef TMON_MODEL_EVENT_HPP
#define TMON_MODEL_EVENT_HPP

#include <array>
#include <cstdint>
#include <string>

namespace tmon {

// The kind of action a record describes. Mirrors the kernel wire enum but is a
// first-class C++ type so the rest of the code never touches raw integers.
enum class EventKind {
  kSyscall,
  kFork,
  kExec,
  kExit,
};

// Number of raw scalar syscall arguments captured, matching the kernel side.
inline constexpr int kSyscallArgs = 6;

// One observed action from a traced process (or its descendants). A plain value
// type: cheap to copy, trivially movable, no ownership surprises.
struct Event {
  EventKind kind = EventKind::kSyscall;
  std::uint64_t ts_ns = 0;   // boot-time nanoseconds, as reported by the kernel
  std::uint32_t pid = 0;     // tgid
  std::uint32_t tid = 0;     // thread id
  std::uint32_t child_pid = 0;      // kFork only
  std::int64_t syscall_nr = -1;     // kSyscall only, else -1
  int exit_code = 0;                // kExit only
  std::array<std::uint64_t, kSyscallArgs> args{};  // kSyscall raw args
  std::string comm;          // command name of the acting task
};

}  // namespace tmon

#endif  // TMON_MODEL_EVENT_HPP
