# Standalone C qualification — 2026-09-21

All **30 standalone programs** have valid target-alert evidence and a clean
same-binary control in **both glibc and musl**: 60 case/runtime pairs. The
measured programs have separate source entry points, build targets, executable
files, and hashes. No runtime case dispatcher is used.

The scope remains **30 of 95 supplied syscall rules**, all among 81 stock-enabled
rules in the fixed Falco snapshot. The detector conditions are unchanged.

## Recorded runs

- Initial randomized matrix: **122 executions** — 60 active programs,
  60 same-binary controls, and 2 empty startup baselines; 116 valid, 6 invalid.
- Recheck of the six cases with invalid attempts: **26 executions**; 24 valid,
  2 invalid. Original attempts are retained rather than replaced.
- Combined: **148 successful behavior/control executions**, **140 valid**,
  **8 invalid**. Every valid active execution matched its exact target rule;
  every valid control remained clear of all 30 selected rules.

All eight invalidations were increments in Falco’s internal
`falcosecurity_scap_n_retrieve_evts_drops_total` counter; they were not
reclassified as detection misses.

Both phase runners returned status 1 because of invalid attempts. Their results
must not be described as a clean collection-health pass. The combined matrix
nevertheless supplies valid positive/control evidence for all 60 pairs: the two
invalid recheck attempts have valid counterparts in the initial matrix.

This is fixture qualification with controls, not the confirmatory experiment
or an estimate of detection accuracy. The diagnostic recheck is explicitly
selected on collection validity and is not a balanced experimental sample.

## What establishes alert attribution

Each program verifies its behavior independently of Falco. The corresponding
`--control` execution loads the same executable with the same hash and path,
in the same fixture environment, but skips its one TTP behavior. Fixture setup
occurs before the measurement window. Alerts are scoped to the fresh container
and matched to the exact target rule.

Controls establish that simply starting these binaries did not trigger the
selected rules in this lab. They do not prove that rule conditions ignore
program names, paths, or command lines. Several stock rules use those fields.
`rule-predicates.json` preserves each selected condition and source file;
`alert-evidence.json` preserves representative target-alert event fields for
every case/runtime pair. Refer to the pinned YAML for macro/list definitions.
These are Falco syscall-event rules, not a binary-content scanning experiment.

A valid alert miss in a later runtime remains valid research data. It does not
automatically disqualify a case whose target has been demonstrated elsewhere.
Behavior failure, failed controls, and collection failure remain separate.

## Files and provenance

- `matrix.csv`: attempts, valid outcomes, and positive/control qualification by
  program and runtime, combining the two labeled phases.
- `runs.csv`: every attempt, including phase, control status, and invalid records.
- `qualification.json`: phase summaries, environment, executable/image hashes,
  source hashes, invalid-attempt details, and private archive SHA-256.
- `dispatcher-pilot/`: **superseded historical results**, not evidence for the
  standalone replacement programs.

The compiled programs and capture runner were staged from `bb9e1c5`. A later
reporting-only correction (`dd787b3`) preserves valid runtime misses in the
suite acceptance decision; it changes neither executable behavior nor captured
records. Its decision is regression-tested and replayed against these records.

The private archive includes all raw logs, behavior/control outputs, health
metrics, validated source, exact container image, compiler/runtime versions,
and detector configuration. It was saved before disposable-lab teardown.
Raw journals may include unrelated host activity and are not committed here.

[Issue #55](https://github.com/bluesentinelsec/telemetry-lab/issues/55) tracks the
broader standalone-program and attribution audit.
[Issue #54](https://github.com/bluesentinelsec/telemetry-lab/issues/54) tracks the
remaining language/platform and experiment-pipeline work.
