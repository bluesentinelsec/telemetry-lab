// Layer 2 — business logic. The boundary between capture and presentation. The
// engine drives an EventSink; concrete sinks (layer 3 formatters) decide how a
// run becomes bytes. Defining the interface here (not in the view layer) keeps
// the dependency arrow pointing inward: the engine depends only on this
// abstraction, never on a specific formatter.
#ifndef TMON_CORE_EVENT_SINK_HPP
#define TMON_CORE_EVENT_SINK_HPP

#include <cstdint>

#include "model/event.hpp"

namespace tmon {

// End-of-run totals, handed to the sink once capture finishes.
struct Summary {
  std::uint64_t total_events = 0;
  std::uint64_t syscall_events = 0;
  std::uint64_t failed_syscalls = 0;  // syscalls that returned an errno
  std::uint32_t processes = 0;        // distinct tgids observed
  std::uint64_t dropped = 0;          // events lost to ring-buffer pressure
  int target_exit_code = 0;
};

class EventSink {
 public:
  virtual ~EventSink() = default;

  // Called once before any events, so a sink can emit a header/preamble.
  virtual void Begin() {}

  // Called for every captured event, in kernel-emitted order.
  virtual void Handle(const Event& event) = 0;

  // Called once after the last event with run totals.
  virtual void End(const Summary& summary) = 0;
};

}  // namespace tmon

#endif  // TMON_CORE_EVENT_SINK_HPP
