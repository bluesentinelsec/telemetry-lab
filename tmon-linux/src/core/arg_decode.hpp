// Layer 2 — business logic. Symbolic decoding of scalar syscall arguments
// (flags, modes, protections) from their raw values — e.g. openat's flags
// argument 0x241 -> "O_WRONLY|O_CREAT|O_TRUNC". Pure and deterministic, so it is
// unit-testable and adds no capture-time overhead (it runs in the formatter, not
// the kernel). Pointer arguments (paths, sockaddrs) are decoded elsewhere, in
// the engine.
#ifndef TMON_CORE_ARG_DECODE_HPP
#define TMON_CORE_ARG_DECODE_HPP

#include <cstdint>
#include <string>

namespace tmon {

// Returns a symbolic rendering of argument `arg_index` of syscall `nr` holding
// raw value `value`, or an empty string when there is no decoder for that
// (syscall, argument) pair (the caller then falls back to hex).
std::string DecodeArg(std::int64_t nr, int arg_index, std::uint64_t value);

}  // namespace tmon

#endif  // TMON_CORE_ARG_DECODE_HPP
