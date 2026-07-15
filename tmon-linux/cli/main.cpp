// tmon CLI. Parses argv into a Config (layer 1), selects a formatter (layer 3),
// and runs the capture engine (layer 2). This file is the only place the three
// layers are wired together and the only consumer of CLI11.
#include <CLI/CLI.hpp>

#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "core/engine.hpp"
#include "model/config.hpp"
#include "view/human_formatter.hpp"
#include "view/json_formatter.hpp"

int main(int argc, char** argv) {
  CLI::App app{"tmon — process-scoped telemetry monitor (eBPF)"};
  app.set_version_flag("--version", "tmon 0.1.0");

  // Everything after tmon's own options is the target command line. Stopping at
  // the first positional lets both `tmon ./x a b` and `tmon -f json ./x` work;
  // `tmon -- ./x` works too (the `--` is dropped below).
  app.prefix_command();

  std::string format = "human";
  app.add_option("-f,--format", format, "Output format: human (default) or json")
      ->check(CLI::IsMember({"human", "json"}));

  std::string output_file;
  app.add_option("-o,--output", output_file,
                 "Write output to FILE instead of stdout");

  bool decode = false;
  app.add_flag("--decode", decode,
               "Resolve pointer/flag arguments (raw args always emitted)");

  bool no_follow = false;
  app.add_flag("--no-follow", no_follow,
               "Do not follow fork/exec descendants of the target");

  bool summary_only = false;
  app.add_flag("-c,--summary", summary_only,
               "Suppress the per-event stream; emit only the summary");

  bool quiet = false;
  app.add_flag("-q,--quiet", quiet, "Suppress the trailing summary line");

  std::uint64_t max_events = 0;
  app.add_option("-n,--max-events", max_events,
                 "Stop after N syscall events (0 = unlimited)");

  std::vector<std::string> meta_kv;
  app.add_option("--meta", meta_kv,
                 "Attach KEY=VALUE metadata to machine-readable output")
      ->take_all();

  CLI11_PARSE(app, argc, argv);

  // The target command line is whatever CLI11 stopped parsing at.
  std::vector<std::string> command = app.remaining();
  if (!command.empty() && command.front() == "--") command.erase(command.begin());
  if (command.empty()) {
    std::cerr << "tmon: no command given\n\n" << app.help();
    return 2;
  }

  tmon::Config config;
  config.command = std::move(command);
  config.format = (format == "json") ? tmon::Format::kJson : tmon::Format::kHuman;
  config.output_file = output_file;
  config.decode = decode;
  config.follow = !no_follow;
  config.summary_only = summary_only;
  config.quiet = quiet;
  config.max_events = max_events;
  for (const auto& kv : meta_kv) {
    auto eq = kv.find('=');
    if (eq == std::string::npos) {
      std::cerr << "tmon: --meta expects KEY=VALUE, got '" << kv << "'\n";
      return 2;
    }
    config.meta[kv.substr(0, eq)] = kv.substr(eq + 1);
  }

  // Resolve the output stream: a file, or stdout.
  std::ofstream file;
  std::ostream* out = &std::cout;
  if (!config.output_file.empty()) {
    file.open(config.output_file, std::ios::out | std::ios::trunc);
    if (!file) {
      std::cerr << "tmon: cannot open output file '" << config.output_file
                << "'\n";
      return 1;
    }
    out = &file;
  }

  // Pick the presentation layer.
  std::unique_ptr<tmon::EventSink> sink;
  if (config.format == tmon::Format::kJson)
    sink = std::make_unique<tmon::JsonFormatter>(*out, config);
  else
    sink = std::make_unique<tmon::HumanFormatter>(*out, config);

  tmon::Engine engine(config);
  int rc = engine.Run(*sink);
  if (rc < 0) return 1;  // setup failure already reported to stderr
  return rc;             // propagate the target's exit code
}
