# Standalone Go qualification — 2026-09-21

All **30 standalone Go programs** have valid behavior and clean same-binary
control evidence with both cgo/glibc and pure-Go static builds. Both Go
configurations triggered **29 of the 30 exact target rules**. The reverse-shell
behavior succeeded but did not trigger its socket-duplication target. A C/glibc
reference demonstrated all 30 targets using the same image, fixtures, helper,
and detector. These are the same 30 selected rules out of 95 supplied Falco
syscall rules, all among the 81 stock-enabled rules; no rule was changed.

Each case has its own source entry point and executable. The shared
[behavior contract](../../behavior-contract.md) fixes operations, inputs, and
checked outcomes. Go 1.24.4 builds the identical source with CGO_ENABLED=1 and
0. ELF and Go build metadata checks verify the claimed configurations. The
cgo anchor ensures glibc linkage; it does not route Go file/socket operations
through libc. Falco 0.45.0 runs on kernel 6.12.107+deb13-cloud-amd64; container
glibc is 2.41-12+deb13u4. Full versions and hashes are in `qualification.json`.

## Alert differences

| Case | C/glibc | Go cgo | Go static |
| --- | --- | --- | --- |
| reverse_shell: target alerts | 3 | 0 | 0 |
| binary_mkdir: target alerts | 1 | 1 | 1 |
| binary_mkdir: additional Modify binary dirs alerts | 1 | 2 | 2 |

The reverse shell returned the exact checked `SHELL_OK` reply and exited
successfully in all three configurations, with healthy collection. C connects
the shell's standard streams directly to the TCP socket. Go supplies a
`net.Conn` to `os/exec`, which uses pipes and copy goroutines. The unchanged
`Redirect STDOUT/STDIN to Network Connection in Container` rule requires a
socket duplication onto descriptors 0, 1, or 2. The Go executions have no
matching alerts. Separate post-qualification strace runs confirm socket
`dup2` in C and pipe `dup3` in Go; see `reverse-shell-traces.md`.

Go can also pass socket descriptors directly. This port deliberately preserves
the existing Go pilot's pipe-relay implementation. The result is an
**implementation-associated C/Go difference**, not evidence that cgo caused a
miss or that every Go reverse shell avoids this rule. Both Go variants use the
same implementation. The valid misses remain in the data and were not rerun
or changed to force alerts. The strace-assisted runs are supplemental mechanism
diagnostics, excluded from qualification counts.

For directory cleanup, the C event is `rmdir`. Go emits an `unlinkat` attempt
that fails with EISDIR, followed by successful `unlinkat` with AT_REMOVEDIR.
Both events match `Modify binary dirs`; see `binary-mkdir-events.json`. The
intended directory-creation target fires once in every configuration. This
shows why extra rule matches and alert counts are retained alongside target
presence. No difference in rule presence or per-rule alert counts was observed
between cgo and static Go in these valid attempts. That does not establish
telemetry equivalence or predict the final experiment.

## Recorded runs

| Phase | Executions | Valid | Health-invalid | Runner exit |
| --- | ---: | ---: | ---: | ---: |
| Initial complete matrix | 183 | 178 | 5 | 1 |
| Explicit collection recheck | 33 | 32 | 1 | 1 |
| Combined | 216 | 210 | 6 | — |

All 216 behavior checks succeeded. Across both phases, 103 active executions
were valid: 101 target hits and two valid misses. Of 111 controls/baselines,
107 were valid and contained no alerts. Together the phases provide valid
active/control evidence for all 90 case/configuration pairs: 30 C reference
pairs and 60 Go pairs. Of those, 88 have a positive target alert and clean
control; the two Go reverse-shell pairs have valid no-alert outcomes.

Six attempts were invalidated by increases in
`falcosecurity_scap_n_retrieve_evts_drops_total`, each by one. The initial run
invalidated C log-truncation control; Go static setid active; and Go static
root-write, cloud-metadata, and EC2-metadata controls. The recheck repeats those
five cases across all three configurations, plus baselines. Its Go static
cloud-metadata active attempt was invalid, but the original active attempt
was valid and its rechecked control was valid. All invalid attempts remain
in `runs.csv` and the archive; neither phase is represented as a clean pass.
These are feasibility checks, not a balanced confirmatory dataset or accuracy
estimate. No further recheck was needed to obtain valid evidence for every
behavior/control pair.

## Functional checks and provenance

Before detector qualification, the final source passed 122/122 functional
executions across both Go configurations. A focused ptrace-attach regression
passed 60/60 executions (20 active, 20 controls, 20 baselines). A superseded
prototype had one attach timeout caused by consuming a child exec stop before
the attach SIGSTOP; the final code waits for the attach stop before detaching.
The prototype failure and diagnostic evidence are archived separately and are
not scored as detection outcomes. All 14 Python evidence/artifact/release tests,
both Go build/vet jobs, and the other CI build configurations passed.

The measured source is commit `f212746916846cd3c14bb461e3ec8c57db427a4c`.
The private archive contains that source, the exact final and prototype images,
binary hashes, build versions, rule/configuration snapshots, complete raw
alerts, behavior outputs, health samples, and supplemental traces. Verification
checked 177 archived source files against Git, all 193 image executable hashes,
and all 216 measured records against their per-execution results before teardown.
The archive SHA-256 is recorded in `qualification.json`.

- `matrix.csv`: all 90 pairs, distinguishing valid behavior/control evidence
  from positive-alert/control evidence.
- `runs.csv`: all 216 measured attempts, validity, matching rules, and counts.
- `qualification.json`: summaries, versions, hashes, and invalid counter changes.
- `alert-evidence.json`: representative target events for all 88 positive pairs.
- `alert-deltas.json`: observed C/Go differences, including non-target counts.
- `reverse-shell-traces.md` and `binary-mkdir-events.json`: mechanism evidence.

Rust, Windows, paired `tmon` event-volume/composition analysis, and the final
experiment remain in [issue #54](https://github.com/bluesentinelsec/telemetry-lab/issues/54).
The broader standalone-program audit remains in [issue #55](https://github.com/bluesentinelsec/telemetry-lab/issues/55).
