# Full matrix validation — September 29, 2026

PRs #68 and #71 were merged before collection. A fresh pair of disposable hosts was deployed with the existing CDK app in us-west-2. Every implemented test/configuration/mode received one accepted repetition. The normal matrix contains 1,714 accepted measurements across 1,815 attempts, with 41 suspect attempts and 60 valid measurements of superseded DNS executables retained separately. No planned slots are missing or duplicated.

| Platform | Cohort | Planned | Accepted | Suspect | Retries |
| --- | --- | ---: | ---: | ---: | ---: |
| Linux | primitives | 104 | 104 | 0 | 0 |
| Linux | composites | 680 | 680 | 0 | 0 |
| Linux | legacy | 56 | 56 | 0 | 0 |
| Windows | primitives | 18 | 18 | 0 | 0 |
| Windows | composites | 832 | 832 | 41 | 33 |
| Windows | legacy | 24 | 24 | 0 | 0 |

## Scope and results

Linux primitives: 13 cases × 8 configurations. Windows primitives: 3 implemented cases × 6 configurations; Windows primitive parity remains outside this validation's implemented scope. Expanded composites: 42 Linux and 52 Windows cases × 8 configurations, each with active and same-binary control execution; Linux adds 8 negative baselines. The 80 retained pilot-program executions are reported separately because they lack the expanded suite's independent behavior assertions.

Expanded active alerts: 750; valid misses: 2; controls with selected-rule alerts: 0. Valid misses: linux-go-cgo/reverse_shell; linux-go-static/reverse_shell. These successful executions with valid collection were accepted without retrying to force an alert. Falco and Hayabusa rules were not modified. Both platforms also completed the bundled tap analysis of accepted primitive telemetry.

## Replacement accounting

The original campaign summaries remain unchanged, including exhausted slots. Separate targeted rechecks and DNS requalification are listed in `summary.json`; only accepted observations from the current program revision are counted in the table above, and the original suspect attempts and successful but superseded DNS observations remain included in attempt totals. Successful observations of the old DNS executables are not mislabeled as suspect. The 64-slot DNS requalification supersedes all prior DNS outcomes, including previously passing controls. The pre-fix targeted recheck verified unchanged program, harness, and collector files and recorded the original campaign/run/attempt references. DNS requalification deliberately changed only the 32 affected executables and their inventory metadata.

## Defects corrected

- Native behavior failures previously bypassed replacement. The engine now uses the same bounded retry policy after normal preparation/cleanup, preserves the original failure classification and raw evidence, and links each replacement. Default: three replacements; disabling retries gives one attempt. Unknown errors, unsafe fixture state, and changed inputs still abort. Valid detection misses remain accepted.
- Short-lived DNS composites omitted the five-second post-I/O lifetime already used by TCP. Four slots exhausted retries, then failed all 16 attempts in an unchanged quiet recheck. Applied the existing five-second hold uniformly to all four DNS cases, all eight runtime configurations, and both active/control modes. All 64 affected slots passed on their first attempt after the correction (32 target alerts and 32 passing controls), replacing the old DNS program revision in the current result view. Before correction, Sysmon DNS events could contain an all-zero ProcessGuid and an unknown process after the short-lived executable exited; attribution checks remain strict. All other program, DLL, collector, rule, and network-fixture bytes remain unchanged.
- The assembled Windows bundle omitted `run-batch.ps1`. Packaging now includes it, and the release validator rejects its absence.

## Live failure validation

On Linux, the required `/etc/shadow` fixture was removed only inside the disposable case container, producing a real native failure. On Windows, the child process environment temporarily hid the command shell from the existing C spawn primitive. No program binary or rule was modified. Both platforms verified successful replacement, disabled retry, and bounded exhaustion. Separate checks corrupted real collector output, interrupted the actual Linux Falco service, and invalidated a shared capture. Replacements recovered valid measurements; every failed attempt remains under `suspect/` and outside accepted analysis data. Detailed counts are in `fault-validation.json`; intentionally disabled/exhausted campaigns correctly remain incomplete.

## Provenance and archive

Initial native component sources match merged main `141656527d826444c1a8aa0c703735470fe61170`. The tested runner and packaging fixes are commit `0d00efa`. The DNS correction is commit `537641e`, built in CI run `36627456071`. The DNS validation bundle preserves every other program and runtime DLL byte from the original bundle; `dns-stage/changes.json` records the 32 changed executable hashes. CI component run IDs, equivalence checks, immutable bundle inventories, source archive, CDK outputs, host inventories, attempt ledgers, raw telemetry, EVTX, and alert evidence are retained at:

`/Users/michaellong/telemetry-lab-data/full-matrix-once-2026-09-29`

Linux archive: 6,164 files / 96,233,158 bytes. Windows archive: 10,544 files / 403,473,138 bytes. Every archived result file was compared with S3 content before teardown, and SHA-256 inventories are retained under `checksums/`.

The task's CDK stack is deleted and both task instances are terminated. No release was published. This is one-repetition operational validation, not additional 200-repetition study collection.
