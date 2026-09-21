# Standalone C++ qualification — 2026-09-21

All **30 standalone C++ programs** produced valid target alerts and have clean
same-binary controls with **both libstdc++ and libc++**: 60 program/library
pairs. Clang++ and source were held constant. The fixed mapping covers **30 of
95 supplied Falco syscall rules**, all among the 81 stock-enabled rules. No
rule conditions, exceptions, or enabled flags were changed.

Each case has its own `main.cpp`, build target, executable, and hash. The
artifact checks verify the complete roster, distinct ELF programs, the intended
C++ dynamic library, and actual imported library symbols. File behavior uses
C++ streams and filesystem operations. Networking and process inspection use
native Linux APIs where C++17 provides no equivalent. See the parent suite
README for the API choices and fixture equivalence to C.

## Recorded runs

| Phase | Executions | Valid | Health-invalid | Runner exit |
| --- | ---: | ---: | ---: | ---: |
| Initial complete matrix | 122 | 119 | 3 | 1 |
| Explicit diagnostic recheck | 14 | 14 | 0 | 0 |
| Combined | 136 | 133 | 3 | — |

The initial matrix contains 60 active programs, 60 same-binary controls, and
two empty startup baselines. All 60 active executions were valid and matched
their exact target rules. Three controls were invalidated by increases in
`falcosecurity_scap_n_retrieve_evts_drops_total`: `dev_file` with libc++, and
`binary_rename` and `udp_exchange` with libstdc++. Their outputs succeeded and
showed no selected alerts, but they remain invalid collection attempts.

The recheck repeats those three cases, active and control, under both libraries,
plus both baselines. It was selected only because of invalid attempts, and all
14 executions passed. Across both phases, all 66 active executions produced
valid target alerts; 67 of 70 controls/baselines were valid and clear of every
selected rule. The original three invalid attempts remain in the archive and
`runs.csv`. The initial phase is **not** represented as a clean collection pass.

This establishes fixture feasibility for all 60 pairs. It is not the final
balanced experiment or an accuracy estimate. No valid target-alert difference
between the two C++ libraries was observed in these qualification runs; this
does not establish telemetry equivalence. A later valid miss remains research
data and must be investigated rather than discarded.

## Attribution and evidence

Every active program independently checks its behavior before reporting
success. Its control starts the identical binary, at the identical path, but
skips the sole TTP behavior. Setup occurs outside the measurement window.
Alerts are attributed to that execution's fresh container and exact rule name.
The shell and benign static helper are fixed across library configurations.

Clean controls show that starting these binaries alone did not trigger the
selected rules here. They do not establish independence from process names,
paths, or command lines: some stock rules deliberately inspect those fields.
`alert-evidence.json` includes representative event fields for all 60 pairs;
`../rule-predicates.json` and the pinned YAML preserve the rule conditions.

- `matrix.csv`: per-case/library attempts, valid target hits, and clean controls.
- `runs.csv`: all 136 attempts, with phase and collection validity.
- `qualification.json`: phase summaries, compiler/runtime versions, hashes,
  and the three invalid attempts with their counter changes.
- `alert-evidence.json`: one valid target-alert example per case/library pair.

The compiled programs and capture runner come from commit `c6b5a70`. The private
archive preserves the validated source, exact container image, binary hashes,
compiler flags and versions, detector configuration, full journals, behavior
outputs, and collector-health samples. Its SHA-256 is recorded in
`qualification.json`. The raw archive was verified locally before lab teardown.
The C qualification is preserved separately in the parent directory.

Go/Rust ports, Windows scope, paired `tmon` telemetry analysis, and the final
experiment remain tracked in [issue #54](https://github.com/bluesentinelsec/telemetry-lab/issues/54).
The broader standalone-program audit remains in [issue #55](https://github.com/bluesentinelsec/telemetry-lab/issues/55).
