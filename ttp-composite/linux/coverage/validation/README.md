# C qualification evidence — 2026-09-21

This directory records qualification of the 30 selected Linux C cases, built
against glibc and musl, on the project's disposable Debian EC2 lab. The measured
source is commit `cfe2068`; subsequent changes in this PR document the evidence.

## Coverage and interpretation

The fixed upstream snapshot contains **95 supplied syscall rules**, including
**81 stock-enabled rules**. The suite explicitly targets **30**: 12 stable,
11 incubating, and 7 sandbox. The detector loads all three preserved collections
and evaluates all matching rules. Rule conditions, exceptions, macros, lists,
and enabled flags remain unchanged. Other observed matches do not expand the
predeclared coverage denominator or substitute for a target rule.

`matrix.csv` reports attempts, valid runs, and valid target hits for each case
and runtime. `runs.csv` retains every scheduled attempt, including invalid
attempts and negative controls. `qualification.json` records environment and
binary provenance, rule/source hashes, the evidence archive digest, and the
specific counter changes associated with invalid attempts.

The final matrix scheduled **186 executions**: 30 cases × 2 C configurations ×
3 repetitions, plus 6 empty controls. All 186 behavior checks succeeded.
**180 executions were valid**, including all 6 controls; **6 were invalidated
by collection-health counters**. All 174 valid target-case executions matched
their exact target rule. Both glibc and musl demonstrated all 30 selected rules
on valid runs. There were no valid target misses, and every negative control
passed. The runner exited with status **1** because it rejects any invalid
attempt; this was not a clean 186-of-186 collection-health pass.

These are fixture-qualification runs, not the dissertation's confirmatory
experiment. They demonstrate selected rule coverage in the two C configurations;
they do not establish equivalence across all runtimes, measure general detector
accuracy, or supply paired event-volume/composition analysis. C++, Go, Rust,
Windows, and main-pipeline telemetry integration remain follow-up work in
[issue #54](https://github.com/bluesentinelsec/telemetry-lab/issues/54).

## Collector policy

An attempt is invalid if behavior fails, the detector restarts, counters reset,
or any captured drop counter increases. This conservative policy includes Falco
internal event-retrieval counters as well as kernel drop counters. All six
invalidations in this matrix were increments in
`falcosecurity_scap_n_retrieve_evts_drops_total`; no kernel buffer-drop increment
was observed during those attempts. A visible
alert does not override an invalid collection-health result. No gate was relaxed
and no invalid attempts were removed to improve the reported coverage.

The runner returns a nonzero status if any attempt is invalid, even when all
selected rules have been demonstrated on other valid attempts. Its process exit
status therefore must be reported separately from the number of qualified rules.

## Fixture corrections before the recorded matrix

Earlier diagnostic passes are preserved in the private archive and are not
pooled into `matrix.csv`:

- `falco30-pilot1`: initial complete pass. It exposed a UDP fixture missing the
  `connect` event required by its target, an executable-path/argv[0] mismatch for
  `/dev/shm`, and a shell-configuration pathname outside the supplied rule list.
  One attempt also encountered a metrics-endpoint failure during detector reload.
- `falco30-fixed-check`: verified those three corrections. The reverse-shell
  behavior completed, but its inherited-socket implementation did not reliably
  generate the target alert.
- `falco30-shell-check`: the shell child creates/connects its own socket before
  redirection; all six target attempts alerted and six negative controls passed.
  This is a fixture correction, not evidence of a runtime-induced difference.

The final detector disables automatic configuration watching and duplicate
syslog output. It uses one stdout JSON stream, the fixed rule files, and
`rule_matching=all`. The final matrix keeps these settings and executable/image
hashes constant across both configurations.

## Archived evidence

The full private archive includes all diagnostic and final runs, behavior output,
attributed alerts, journal windows, collector metrics, randomized order, compiler
and runtime versions, ELF interpreter checks, detector configuration, validated
source, and the exact container image. Raw journal windows can include unrelated
host activity and are intentionally not committed here. The archive SHA-256 in
`qualification.json` identifies the preserved evidence package.
