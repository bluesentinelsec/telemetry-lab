// Layer 2 — business logic. The capture engine: it takes a resolved Config,
// spawns the target under a from-birth BPF filter scoped to the target's process
// tree, pumps the resulting events into an EventSink, and returns the target's
// exit code. It owns all the OS/BPF machinery so neither the model nor the view
// layer ever sees a file descriptor.
#ifndef TMON_CORE_ENGINE_HPP
#define TMON_CORE_ENGINE_HPP

#include "core/event_sink.hpp"
#include "model/config.hpp"

namespace tmon {

class Engine {
 public:
  explicit Engine(const Config& config) : config_(config) {}

  // Runs the target to completion, streaming events to `sink`. Returns the
  // target's exit code on success, or a negative value if the run could not be
  // set up (BPF load/attach failure, spawn failure, etc.). On failure a
  // diagnostic is written to stderr.
  int Run(EventSink& sink);

 private:
  const Config& config_;
};

}  // namespace tmon

#endif  // TMON_CORE_ENGINE_HPP
