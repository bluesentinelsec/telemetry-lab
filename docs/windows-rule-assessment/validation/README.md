# Windows expansion qualification — October 8, 2026

All four additions qualified in all eight Windows configurations, bringing the
selected Windows scope to **56 exact target rules** out of **2,269 enabled
rules** in the pinned Hayabusa 4.1.0 corpus (4,987 supplied definitions).
This campaign covers Windows only. Historical datasets remain unchanged.

| Cohort | Cases | Configurations | Repetitions per mode | Exact-rule hits | Clean controls |
| --- | ---: | ---: | ---: | ---: | ---: |
| C reference pilot | 4 | 1 (C UCRT) | 1 | 4 | 4 |
| New-case qualification | 4 | 8 | 3 | 96 | 96 |
| Shared-helper regression | 2 | 8 | 3 | 48 | 48 |

The matrix accepted **288/288 planned observations**. Its preserved campaign
summary reports 0 suspect attempts and 0
retries. The eight-observation reference pilot is separate, not pooled into the
three-repetition matrix. The two regression cases are `double_extension_execute`
and `ads_executable`; they exercise the modified helper's original zero-argument
behavior and its use as a benign executable payload.

## What was demonstrated

| New case | Exact bundled rule ID | Observed target event and independent behavior evidence |
| --- | --- | --- |
| `unicode_child_arguments` | `efe8a84a-0bef-c646-b13a-5a3cbe2b01b9` | Event 1 records the actual benign child argument containing U+00A0. The fixed C helper verifies its exact UTF-16 argument and returns 43; scoring follows the measured parent's GUID to the child. |
| `ads_provenance_contents` | `ecb9ed8e-9e96-85bd-a68e-c86d68005053` | Event 15 includes the synthetic Zone.Identifier text and numeric-IP URL. Native byte readback succeeds. This is stream-content detection; no download or network connection occurred. |
| `raw_owned_volume_read` | `f4ca1a32-116e-1b6b-6d74-233983928c00` | Event 9 identifies the measured process's raw device read. The probe verifies the first 512 known bytes of a fresh, read-only VHD. All 25 batch fixtures were detached and removed with unchanged full-image hashes. |
| `signed_system_library_load` | `1b615dd1-9d33-03df-fb06-d8fc0ee7d654` | Event 7 identifies genuine System32 RstrtMgr.dll. Native module-path checks pass; the harness records its valid Microsoft signature and frozen hash. No Restart Manager operation is invoked. |

Every accepted control is free of attributable alerts against **all 56 selected
rules**, not only its paired target. Exact IDs, record IDs, event fields, process
GUIDs, and full raw EVTX/Hayabusa outputs are retained. All 25
batches were independently reanalyzed locally from archived events and alerts;
collection health, completeness, and attribution passed.

No target-outcome difference was observed among these configurations. That does
not establish equivalent event volume, event composition, or general detector
effectiveness. These are purposively selected, C-detectable fixtures and bounded
qualification runs, not the 200-repetition confirmatory dataset. Native API
fallbacks and the shared helper limit where runtime-mediated differences can arise.

## Frozen inputs and reproducibility

- Native binaries: [CI 37805868992](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/37805868992), source `2726bac270cd4b5322a97960786400161b58e849`; all 17 jobs passed. The later documentation-only commits did not change native implementations.
- Harness source: `6bdfddd9eb635925db7df7ad47b01eda360bdb27`. The archived selection labels the four candidates pending; the PR changes their status only after examining qualification evidence.
- Infrastructure: existing telemetry-lab CDK app, Windows-only stack `WindowsExpansionQualification`, default AWS credentials with explicit us-east-1, c7i.xlarge in us-east-1b, Windows Server 2025 build 26100, AMI `ami-00d8aa800578d8b12`.
- Sysmon 15.22 SHA-256: `83d31f2478dc6716cfdbf69e5c384bf043072b5f0d8d7b2eea365f709fda4352`.
- Sysmon profile SHA-256: `e7eac2830897792eb7621ae0fd6b5ccfa6827db532c8e51940dddcf182fedb21`. The authored profile and stock rule predicates were unchanged.
- Hayabusa executable SHA-256: `a9603a988b6a8360684dde95d9a65b1793e9415a6ee7cd8b40c601cf3036e623`. Every batch verifies all 4,987 inventoried rule-file hashes and the pinned evaluator/filter configuration before scoring.
- Fixed C reference helper SHA-256: `176d4810f76952387b32ab8f0dde49e79ce407f4e1f72b8aa55a73031c1fdb99`; identical across every live configuration. The system-library hash and remaining provenance are in [summary.json](summary.json).

The first deployment hit an AZ capacity shortage; a concurrent retry hit the VPC
limit during rollback. Failed stacks were removed before the successful deploy.
The user-requested pause interrupted the final bootstrap step. On resumption,
the authored Defender-removal step was completed, the host rebooted, and absence
of Defender plus running Sysmon were verified before staging or measuring.
These setup events are separate from qualification observations.

Reproduce using `scripts/coverage-expansion/lab.py` with the saved stack outputs:
`stage --ci-run 37805868992`, then `run --phase c-reference --config windows-c-ucrt
--repetitions 1 --no-retry` with the four new `--case` arguments. After verifying
that pilot, use `run --phase qualification --repetitions 3` with those four cases
plus `double_extension_execute` and `ads_executable`. All eight configurations
are selected by default. Use `collect`, then `scripts/coverage-expansion/summarize.py`
on each campaign. Preserve valid misses and all failed attempts; do not retry
merely to obtain an alert.

## Evidence and scope

- [Reference pilot](c-reference.json) and [per-case counts](c-reference.csv).
- [Full matrix](qualification.json) and [per-case/configuration counts](qualification.csv).
- [Target event receipts](target-event-receipts.json): selected raw target fields for every new-case hit, including the separate pilot.
- [Summary and provenance](summary.json): cohort counts, common hashes, fixture checks, and archive verification receipt.
- Local raw evidence: `/Users/michaellong/telemetry-lab-data/windows-expansion-2026-10-08/raw/windows`.

The new raw/SSM archive contains **3,353 verified files /
206,992,588 bytes**. Local bytes were compared to S3 object checksums
(or downloaded content for multipart objects), and a SHA-256 manifest was saved
outside the repository. Its digest is in the summary. Existing historical raw
data was left in place; raw captures and binaries are not committed to Git.

The original 52-case qualification remains in its historical report. Combined
scope is 56 rules, 13 cataloged behavior families, and 17 permitted event IDs.
Only the raw-read case adds an event family/ID; the other additions broaden
argument, stream-content, and library-loading coverage. Permitted event IDs do
not establish that every alternative event pathway was exercised.
