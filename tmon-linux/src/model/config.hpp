// Layer 1 — data model. The fully-resolved run configuration: what to run, what
// to capture, and how/where to emit it. The CLI (layer 3) builds one of these;
// the engine (layer 2) consumes it. Nothing here parses argv or knows CLI11.
#ifndef TMON_MODEL_CONFIG_HPP
#define TMON_MODEL_CONFIG_HPP

#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace tmon {

// Presentation format for the event stream.
enum class Format {
  kHuman,  // strace-like, human-readable (default)
  kJson,   // one JSON object per line (JSONL)
};

struct Config {
  // The target program and its arguments (argv[0] is the program). Required.
  std::vector<std::string> command;

  Format format = Format::kHuman;

  // Output destination. Empty means stdout.
  std::string output_file;

  // Resolve pointer/flag arguments into readable strings (opt-in). Raw scalar
  // args are always emitted regardless.
  bool decode = false;

  // Follow fork/exec descendants of the target. On by default (--no-follow).
  bool follow = true;

  // Suppress the human-readable per-event stream; only emit the summary.
  bool summary_only = false;

  // Suppress the trailing summary line.
  bool quiet = false;

  // Stop after this many syscall events (0 = unlimited).
  std::uint64_t max_events = 0;

  // Free-form metadata to stamp onto machine-readable output (--meta k=v).
  std::map<std::string, std::string> meta;
};

}  // namespace tmon

#endif  // TMON_MODEL_CONFIG_HPP
