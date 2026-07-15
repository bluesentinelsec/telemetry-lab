// Layer 3 — view/presentation. Renders the event stream in a human-readable,
// strace-like form to a std::ostream. Implements the core EventSink interface so
// the engine can drive it without knowing anything about formatting.
#ifndef TMON_VIEW_HUMAN_FORMATTER_HPP
#define TMON_VIEW_HUMAN_FORMATTER_HPP

#include <cstdint>
#include <ostream>

#include "core/event_sink.hpp"
#include "model/config.hpp"

namespace tmon {

class HumanFormatter : public EventSink {
 public:
  HumanFormatter(std::ostream& out, const Config& config)
      : out_(out), config_(config) {}

  void Begin() override;
  void Handle(const Event& event) override;
  void End(const Summary& summary) override;

 private:
  // Relative seconds since the first event, for readable timestamps.
  double RelativeSeconds(std::uint64_t ts_ns);

  std::ostream& out_;
  const Config& config_;
  std::uint64_t first_ts_ns_ = 0;
  bool have_first_ts_ = false;
};

}  // namespace tmon

#endif  // TMON_VIEW_HUMAN_FORMATTER_HPP
