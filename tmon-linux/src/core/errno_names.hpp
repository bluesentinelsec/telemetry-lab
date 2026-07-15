// Layer 2 — business logic. Maps errno numbers to their symbolic names (EPERM,
// ENOENT, ...). Table generated at build time from <asm-generic/errno*.h> so it
// matches the host ABI. Used to make syscall failures human-readable.
#ifndef TMON_CORE_ERRNO_NAMES_HPP
#define TMON_CORE_ERRNO_NAMES_HPP

namespace tmon {

// Returns the symbolic name for `num` (a positive errno), or nullptr if unknown.
const char* ErrnoName(int num);

}  // namespace tmon

#endif  // TMON_CORE_ERRNO_NAMES_HPP
