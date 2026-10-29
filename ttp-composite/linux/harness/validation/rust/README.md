# Standalone Rust qualification — 2026-09-21

All **30 standalone Rust programs** produced valid exact-target alerts and have
clean same-binary controls with **both static GNU/glibc and musl builds**:
60 Rust case/configuration pairs. A C/glibc reference provides the same evidence
for all 30 cases in the identical image on the same host. The mapping still
covers **30 of 95 supplied Falco syscall rules**, all among the 81 stock-enabled
rules. No rule conditions, exceptions, enabled flags, or target names changed.

Every case has its own `main.rs`, Cargo binary target, executable, and hash.
The [behavior contract](../../behavior-contract.md) fixes the operation, paths,
payloads, helper, and independently checked outcome. Rust 1.98.1 and source are
held constant; both target configurations use static CRT linking. Artifact
checks verify the full roster, distinct ELF files, single-case markers, static
linkage, compile-target markers, and actual GNU/musl startup symbols.

## Alert outcomes and observed events

No difference in **rule presence or per-rule alert counts** was observed among
C/glibc, Rust GNU, and Rust musl across the valid active attempts. This includes
additional rule matches, not just each case's intended target. Every valid
control/baseline contained no alerts. `alert-deltas.json` is therefore empty.

Both Rust reverse shells returned the checked `SHELL_OK` reply and produced
three socket-duplication target alerts per valid active execution, matching C.
Their target events show `dup2` with `fd.type=ipv4`. This Rust implementation
uses direct `TcpStream`/`OwnedFd`/`Stdio` conversions, following the existing
Rust pilot. It does not use the Go port's pipe relay. The prior Go qualification
retains its valid reverse-shell misses separately; these Rust results do not
replace or invalidate that evidence.

Matching alerts do **not** mean matching telemetry. Representative target
alerts show:

- In 15 file-related cases, Rust GNU emits `openat` while Rust musl emits `open`.
  The selected rules still alert in both configurations.
- The hard-link case emits `linkat` in both Rust builds and `link` in C.

`target-event-types.json` lists every case's representative target event and
these differences. These are observed Falco alert fields, not a complete
syscall trace or event-volume/composition dataset. The Rust target standard
libraries and linked libc differ together; this qualification does not isolate
libc alone or establish a general detection-equivalence result.

## Recorded runs

| Phase | Executions | Valid | Health-invalid | Runner exit |
| --- | ---: | ---: | ---: | ---: |
| Initial complete matrix | 183 | 177 | 6 | 1 |
| Explicit collection recheck | 27 | 26 | 1 | 1 |
| Combined | 210 | 203 | 7 | — |

All 210 behavior checks succeeded. Of 102 active attempts, 99 were valid and
all 99 produced their exact target alerts. Of 108 controls/baselines, 104 were
valid and alert-free. Together the phases provide valid positive-alert/control
evidence for all 90 case/configuration pairs, plus a valid baseline for each
configuration. This is fixture qualification, not the final balanced experiment
or an accuracy estimate.

Every invalid attempt had a one-count increase in
`falcosecurity_scap_n_retrieve_evts_drops_total`. The six initial invalids were:

- Rust GNU: `proc_environ` control, startup baseline, `drop_execute` active,
  and `metadata_ec2` active.
- C/glibc: `reverse_shell` control and startup baseline.

The recheck repeated those four named cases across all three configurations,
with their same-binary controls and all three baselines. Its Rust GNU
`proc_environ` active attempt was invalid; that case already had a valid
initial active attempt, and its rechecked control was valid. The other missing
counterparts and both invalidated baselines received valid recheck evidence.
All seven invalid attempts remain in `runs.csv` and the raw archive. Neither
phase is described as an entirely clean collection pass. The collector-health
policy and cause of these counters remain follow-up work in issue #54.

## Versions, checks, and evidence

The source and capture runner are commit
`9a2d07bb2d1f234f7e40b44d0e022ef437f4fd02`. Rust is 1.98.1; the native binding
crate is pinned to `libc` 0.2.177. GNU links host `libc6-dev` 2.41-12+deb13u4;
musl uses the pinned Rust target's bundled static library. The archive includes
hashes of the host static glibc archive and both Rust target library trees.
Falco is 0.45.0 on kernel 6.12.107+deb13-cloud-amd64.

Both Rust builds passed strict Clippy and actual-artifact verification. The
preliminary functional matrix passed 122/122 executions. All 15 Python
artifact/evidence/release tests and all 15 CI jobs passed. Release packaging
preserves all eight implemented Linux configurations and keeps the expanded
suite separate from the existing legacy composites.

The private raw archive preserves the exact source, image, all compiled
programs, build logs, toolchain and runtime metadata, rule/config snapshots,
full alerts, behavior outputs, health samples, and recheck selection reason.
Before teardown, verification checked 252 source files against Git, all 257
image executable hashes, and all 210 per-execution results. Its SHA-256 is in
`qualification.json`.

- `matrix.csv`: all 90 case/configuration pairs and their valid alert/control evidence.
- `runs.csv`: every measured attempt, validity, matching rules, and counts.
- `qualification.json`: summaries, versions, hashes, and invalid counter changes.
- `alert-evidence.json`: one valid target-alert example per case/configuration.
- `alert-deltas.json`: observed rule-presence/count differences (none here).
- `target-event-types.json`: representative target-event syscall differences.

Windows, paired `tmon` event-volume/composition integration, environment freeze,
and confirmatory collection remain in
[issue #54](https://github.com/bluesentinelsec/telemetry-lab/issues/54).
The broader standalone-program audit remains in
[issue #55](https://github.com/bluesentinelsec/telemetry-lab/issues/55).
