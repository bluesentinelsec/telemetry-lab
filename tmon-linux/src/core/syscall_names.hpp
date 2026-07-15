// Layer 2 — business logic. Maps x86-64 syscall numbers to their names. The
// table is generated at build time from the host's <asm/unistd_64.h> (see
// cmake/gen_syscalls.sh), so it always matches the kernel ABI tmon is built for
// rather than a hand-maintained list that drifts.
#ifndef TMON_CORE_SYSCALL_NAMES_HPP
#define TMON_CORE_SYSCALL_NAMES_HPP

#include <cstdint>

namespace tmon {

// Returns the syscall name for `nr`, or nullptr if unknown. The returned
// pointer is to static storage and outlives any caller.
const char* SyscallName(std::int64_t nr);

}  // namespace tmon

#endif  // TMON_CORE_SYSCALL_NAMES_HPP
