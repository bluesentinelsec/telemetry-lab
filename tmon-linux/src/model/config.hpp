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

  // Decode pointer arguments (paths, sockaddrs) by reading target memory. On by
  // default: passive kernel-side reads do not change the target's behavior. Raw
  // scalar args are always emitted regardless. Cleared by --no-decode.
  bool decode = true;

  // Capture syscall return values and errno by hooking sys_exit. On by default
  // (passive). Cleared by --no-returns.
  bool capture_returns = true;

  // Follow fork/exec descendants of the target. On by default (--no-follow).
  bool follow = true;

  // Suppress the human-readable per-event stream; only emit the summary.
  bool summary_only = false;

  // Suppress the trailing summary line.
  bool quiet = false;

  // Stop after this many syscall events (0 = unlimited).
  std::uint64_t max_events = 0;

  // Ring-buffer size in MiB (0 = use the built-in default). Raise it for very
  // high-syscall-rate workloads if the run reports dropped events.
  unsigned buffer_mb = 0;

  // Free-form metadata to stamp onto machine-readable output (--meta k=v).
  std::map<std::string, std::string> meta;
};

}  // namespace tmon

#endif  // TMON_MODEL_CONFIG_HPP
