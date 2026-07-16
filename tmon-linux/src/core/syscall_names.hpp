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

// Returns the argument count (arity) for `nr`, or -1 if unknown. Lets callers
// print only the real arguments instead of all six captured registers.
int SyscallArity(std::int64_t nr);

// True for syscalls whose return value is an address (mmap/brk/mremap/shmat), so
// a human formatter can render the result in hex rather than as a huge decimal.
bool SyscallReturnsPointer(std::int64_t nr);

}  // namespace tmon

#endif  // TMON_CORE_SYSCALL_NAMES_HPP
