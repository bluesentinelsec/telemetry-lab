// Layer 2 — business logic. Translates the kernel wire record (tmon_event, the
// on-ring-buffer POD shared with the BPF program) into the domain model
// (tmon::Event). Kept separate from the engine so it can be unit-tested without
// loading BPF or touching a kernel: pure, deterministic, no I/O.
#ifndef TMON_CORE_EVENT_DECODE_HPP
#define TMON_CORE_EVENT_DECODE_HPP

#include "model/event.hpp"

// C wire struct, declared in bpf/tmon_event.h (global namespace).
struct tmon_event;

namespace tmon {

// Build a domain Event from one kernel wire record.
Event DecodeEvent(const ::tmon_event& wire);

}  // namespace tmon

#endif  // TMON_CORE_EVENT_DECODE_HPP
