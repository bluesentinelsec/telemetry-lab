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
// type: cheap to copy, trivially movable, no ownership surprises. For a syscall,
// the engine pairs the kernel's enter and exit records into one of these, so a
// single Event carries the arguments, the result, and the duration.
struct Event {
  EventKind kind = EventKind::kSyscall;
  std::uint64_t ts_ns = 0;   // boot-time nanoseconds (enter time for a syscall)
  std::uint32_t pid = 0;     // tgid
  std::uint32_t tid = 0;     // thread id
  std::uint32_t child_pid = 0;      // kFork only
  std::int64_t syscall_nr = -1;     // kSyscall only, else -1
  int exit_code = 0;                // kExit only
  std::array<std::uint64_t, kSyscallArgs> args{};  // kSyscall raw args
  std::string comm;          // command name of the acting task

  // Result of a syscall, populated once the exit record is paired in.
  bool has_ret = false;
  std::int64_t ret = 0;      // raw return value
  int error = 0;             // errno if the call failed (ret in [-4095,-1]), else 0

  // Wall-clock cost of the syscall (exit_ts - enter_ts). Only meaningful when
  // has_ret is true.
  bool has_duration = false;
  std::uint64_t duration_ns = 0;

  // Decoded pointer arguments (empty/absent when not applicable or --no-decode).
  std::string path;          // decoded path argument, if any
  int path_argno = -1;       // which args[] index the path came from
  std::string sockaddr;      // decoded "ip:port" (or description), if any
  int sockaddr_argno = -1;   // which args[] index the sockaddr came from
};

}  // namespace tmon

#endif  // TMON_MODEL_EVENT_HPP
