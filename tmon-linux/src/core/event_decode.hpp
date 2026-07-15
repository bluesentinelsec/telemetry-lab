// Layer 2 — business logic. Translates the kernel wire record (tmon_event, the
// on-ring-buffer POD shared with the BPF program) into the domain model
// (tmon::Event). Kept separate from the engine so it can be unit-tested without
// loading BPF or touching a kernel: pure, deterministic, no I/O.
#ifndef TMON_CORE_EVENT_DECODE_HPP
#define TMON_CORE_EVENT_DECODE_HPP

#include <cstddef>
#include <string>

#include "model/event.hpp"

// C wire struct, declared in bpf/tmon_event.h (global namespace).
struct tmon_event;

namespace tmon {

// Build a domain Event from one kernel wire record. A SYS_ENTER yields a
// kSyscall event with args and decoded pointers (has_ret=false); a SYS_EXIT
// yields a kSyscall event with the result (has_ret=true). The engine pairs the
// two by thread. fork/exec/exit map straight through.
Event DecodeEvent(const ::tmon_event& wire);

// Render a raw sockaddr (as captured from target memory) into "ip:port" for
// AF_INET/AF_INET6, "unix:/path" for AF_UNIX, or "family=<N>" otherwise. Returns
// empty if there are too few bytes to read the address family.
std::string DecodeSockaddr(const unsigned char* bytes, std::size_t len);

}  // namespace tmon

#endif  // TMON_CORE_EVENT_DECODE_HPP
