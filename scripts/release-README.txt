telemetry-lab — pre-compiled bundle
===================================

A development release of the telemetry-lab study tooling: the process-scoped
telemetry monitor (tmon), the analysis pipeline (tap), and the TTP primitives
built across every in-scope toolchain/runtime configuration.

Layout
------
  tmon/            the telemetry monitor for this OS
  tap/             the telemetry analysis pipeline for this OS
  ttp-primitives/  one folder per config, each with: empty, file_io, spawn
  substrate/       per-config static substrate-verification records
  manifest.json    version, commit, and the configs in this bundle

Running a primitive under the monitor
-------------------------------------
Linux (needs root / CAP_BPF; e.g. via SSM RunCommand, which runs as root):
  ./tmon/tmon --format json -o run.jsonl \
      --meta os=linux --meta config=linux-c-glibc --meta primitive=spawn \
      --meta iteration=1 -- ./ttp-primitives/linux-c-glibc/spawn

Windows (needs Administrator/SYSTEM; SSM RunCommand runs as SYSTEM):
  .\tmon\tmon.exe --format json -o run.jsonl `
      --meta os=windows --meta config=windows-c-ucrt --meta primitive=spawn `
      --meta iteration=1 -- .\ttp-primitives\windows-c-ucrt\spawn.exe

Analyzing collected data
------------------------
  ./tap/tap run <dir-of-raw-jsonl> -o results
  # -> results/{normalized.jsonl, analysis.json, figures/*.png, report.md}

Notes
-----
- Linux tmon needs glibc, libelf1, zlib1g, libzstd1 (present on the lab AMI).
- Windows binaries are unsigned; on the lab host Defender is disabled and
  execution is non-interactive (SSM), so SmartScreen does not prompt. If a file
  is blocked by Mark-of-the-Web after unzip, clear it with:
    Get-ChildItem -Recurse | Unblock-File
- Cross-OS analysis needs both hosts' JSONL co-located for one `tap run`.
