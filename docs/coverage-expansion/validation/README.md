# Live coverage-expansion qualification

The disposable `CoverageExpansion20260928` stack was deployed through the existing
CDK application on 2026-09-28 (America/New_York). Both platforms used one
m6i.large host and all eight runtime configurations. Programs ran serially;
only capture/export/replay was batched. These are development qualification
runs, not the proposed 200-repetition confirmatory dataset.

Rules remained pinned and unmodified. Linux used the existing Falco 0.45.0
collector-health build and the 95-rule snapshot recorded in `manifest.json`.
Windows used the pinned Hayabusa 4.1.0 executable and release corpus, verified
against all 4,987 file hashes before replay. Each accepted observation requires
independent behavior success, collection health and attribution to the measured
program. Missing an alert is not a reason to retry.

## Linux final results

All **2,040/2,040 planned measurements** were accepted: **1,002 target hits,
1,032 clean controls/baselines, and six valid misses**. There were no suspect
attempts or retries. The misses were the known Go reverse-shell outcome in
both configurations, three repetitions each. All twelve additions produced
**288/288 target hits and 288/288 clean controls** across eight configurations.
The complete Linux archive contains 16,552 files (258,678,618 bytes); every file
was checked against its S3 content checksum and a local SHA256 manifest was saved.
One stale local setup log was refreshed; its prior contents were retained.
See [per-case counts](linux-qualification.csv) and [summary and hashes](linux-qualification.json).

Windows final qualification is still in progress; final totals will be added here.

## Inputs and reproducibility

- Linux native binaries: [CI run 36515492164](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/36515492164), source `8ceef34e60712624e61ea23a273b6b871dea26f0`.
- Windows final native binaries: [CI run 36517181930](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/36517181930), source `749586b`.
- Both builds passed all 17 jobs: sixteen native configuration builds and the evidence tests.
- Staged bundle manifests preserve per-program hashes, compiler/runtime provenance and fixed helper hashes. Stage receipts preserve complete payload hashes; campaign plans freeze the exact staged inputs.
- The launcher, fixtures, captures, detector replay, suspect-run quarantine and bounded replacement are automated. The experiment CLI supports `--repetitions 200`, `--max-retries` and `--no-retry`.

The raw archive includes native stdout/stderr, manifests, attempt records,
collector-health reports, Linux Falco events, Windows EVTX/JSON/CSV, local DNS
request logs, deployment outputs, SSM commands and stage receipts. Compact
qualification tables and hashes accompany this report.

## Defects and prototype observations retained

1. The first Linux namespace-creation prototype completed in C/C++/Rust but
   missed the stock rule after gaining namespace capabilities. Go's multithreaded
   process failed the operation yet generated an alert. Those are six valid
   misses and two invalid behaviors, not proof of equivalent successful behavior.
   Before qualification, all four implementations were replaced together with an
   explicitly **denied network-namespace request**: assert `EPERM` and unchanged
   namespace identity. The original 192-attempt evidence is retained.
2. Windows PowerShell 5.1 cannot use the selected .NET file API to create an
   alternate stream. The first 480-slot expansion preflight aborted its first
   batch (48 quarantined slots; 432 never started). Stream creation now uses
   PowerShell's explicit `-Stream` support.
3. All eight Windows configurations successfully deleted the alternate stream,
   but the original metadata-based postcondition inspected the surviving carrier
   file. The eight active attempts failed validation; eight controls passed.
   Each language now checks that the stream exists before deletion, cannot be
   opened afterward, and that its carrier remains. The original attempts remain
   quarantined; their alerts are not counted as qualified successes.
4. A subsequent C/UCRT preflight of the other 52 Windows cases completed all 104
   active/control slots, with four quarantined attribution failures successfully
   replaced. There were 51 target hits, 52 clean controls and one valid miss.
   In that miss, Sysmon recorded a successful `_ldap.telemetry-lab.test` lookup
   with the correct owner GUID but `Image=<unknown process>`. The stock LDAP-
   discovery rule explicitly filters that image value. This is a sensor-metadata
   limitation; it is not evidence that the runtime alone caused the miss.

5. An earlier UTF-8 manifest was decoded as ANSI by Windows PowerShell 5.1,
   leaving a right-to-left filename fixture outside the harness's mistaken
   cleanup path. The next campaign correctly refused that pre-existing path.
   JSON inputs now explicitly use UTF-8; file targets are checked with literal
   paths and successful native creation must agree with the manifest path.
   Recovery removed only the exact owned path after its SHA256 matched the
   archived fixed helper (`41fd80ad721b186d585d05ff0836ea1c6836563eec26f08c3a2cd8cf6b026930`).
   The partial campaign and recovery receipts are retained. CI now uses Windows
   PowerShell 5.1 and forces raw Unicode manifest text to cover this regression.

CI also caught an already-owned Windows `ErrorHandler.cmd` fixture path; the
harness refused to overwrite it. The candidate was replaced with creation of
an owned inert `.sdb` file, never installed as a shim. The rclone path was fixed
to an owned Public-profile fixture so SYSTEM execution satisfies the actual
stock path predicate. Both selection changes are reflected in issue #70.

## Interpretation

Primary target counts are distinct selected rule IDs. Incidental matches do not
increase those counts. Multiple indicator-based rules may use the same OS
mechanism, so the totals are not independent attack mechanisms or a random
sample of product-wide detection performance. Process access, remote thread,
namespace, BPF and other direct-API cases have narrower opportunities for
standard-library effects than file, process-launch and resolver cases.

A target can remain in scope when a valid implementation misses it, provided the
behavior is equivalent and its rule mapping is demonstrated. Valid misses,
control alerts and collector/attribution failures are reported separately.
