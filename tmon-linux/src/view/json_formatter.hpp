// Layer 3 — view/presentation. Renders the event stream as JSONL (one JSON
// object per line) to a std::ostream. Every line carries a "record" field so a
// consumer can tell meta/event/summary rows apart. Implements EventSink.
#ifndef TMON_VIEW_JSON_FORMATTER_HPP
#define TMON_VIEW_JSON_FORMATTER_HPP

#include <ostream>

#include "core/event_sink.hpp"
#include "model/config.hpp"

namespace tmon {

class JsonFormatter : public EventSink {
 public:
  JsonFormatter(std::ostream& out, const Config& config)
      : out_(out), config_(config) {}

  void Begin() override;
  void Handle(const Event& event) override;
  void End(const Summary& summary) override;

 private:
  std::ostream& out_;
  const Config& config_;
};

}  // namespace tmon

#endif  // TMON_VIEW_JSON_FORMATTER_HPP
