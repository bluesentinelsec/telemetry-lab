# Windows Rust live qualification

Both **dynamic and static MSVC CRT configurations demonstrate the same 23 exact targets out of 2,269 enabled Sysmon rules**, with clean same-binary controls. All 24 C/C++/Go candidates have standalone Rust implementations. The `.onion` candidate fails the unchanged successful-resolution requirement in both builds and remains outside the 23-rule qualified scope.

## Results

The six non-network/TCP/ordinary-DNS campaigns contain **92 executions: 46 attributable target alerts and 46 clean controls**, with no valid misses, failed controls, attribution failures or invalid attempts. Each configuration covers 17 non-network cases, five TCP cases and one ordinary DNS case.

The two `.onion` diagnostic campaigns add four executions: two clean controls and two invalid active attempts. All **96 planned executions were recorded**, yielding 46 alerts, 48 clean controls and two invalid attempts overall. An alert from an unsuccessful `.onion` lookup is not credited as a qualified positive. No rule or behavior contract was weakened, and no rechecks or substituted attempts were needed.

An exploratory comparison of all attributable rule-ID alert counts across the 46 paired case/control comparisons found **no differences** between Rust configurations. See `secondary-alert-comparison.json` and its reproducible script. Incidental rules do not expand the 23-rule numerator. Identical alerts do not imply identical telemetry, and these single qualification runs do not establish repeated-experiment reliability or causal runtime equivalence.

## Artifact and runtime verification

Live artifacts and the shared runner come from commit `e753bfc685990769f1b51f540e1a930355628529`, [CI run 35789991409](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/35789991409). Both builds use Rust 1.98.1, windows-sys 0.59.0, the `x86_64-pc-windows-msvc` target, MSVC tools 14.51.36231, linker 14.51.36256.0 and Windows SDK 10.0.26100.0. Only the declared CRT linkage flag differs. CI passed all 17 jobs, including 17 non-network behavior/control pairs in each Rust build. Local checks passed 18 Windows analyzer/verifier tests and 15 Linux analyzer/release tests.

The dynamic configuration imports UCRT API sets and VCRUNTIME140.dll; its actual bundled VCRUNTIME140.dll has SHA-256 `d1f4225df2cd877dbf130d5668a021dce3f94118455ff5ec952061c30afc9ce7`. All 48 dynamic launches have a matching measured-process image-load record for that DLL at the staged path. Static executables have no direct CRT DLL imports and require no bundled runtime DLLs. Both configurations still depend on Windows system DLLs; native APIs and fixed fixture modules can load additional system libraries independently of the program's CRT linkage.

All **96 staged executable hashes match their CI manifests** and have one attributed process-start event. Sysmon reports a different executable hash in **42 of 96** process-start records, consistent with the repeated/stale image-hash observations already retained in Go qualification. These sensor fields are preserved verbatim. `runtime-evidence.json` records expected/staged/Sysmon hashes, exact start records, loaded runtime dependencies and system CRT observations. `verify-runtime.py` reproduces the audit. The precise sensor mechanism remains unresolved; independent staged-file verification and process-GUID attribution remain necessary. The selected target predicates do not depend on image hashes.

## Equivalence and collection

Every program has one behavior and an in-program `--control`; there is no dispatcher. Fixed paths, values, fixture contents, echo/RDP bytes, five-second TCP lifetime and exact target rule IDs match the other languages. File and socket operations use Rust standard libraries; registry, creation-time, named-pipe and module-loading operations use Windows bindings. Rust's ordinary resolver may request both address families, unlike C's AF_INET hint; the local fixture still requires the exact IPv4 answer. In these captures the server logged an A query for `api.ipify.org` in both Rust configurations. No custom resolver or additional network service was introduced.

Live helper/module/server binaries are the identical archived C reference fixtures from CI run 35729429141, not the differently compiled fixtures used for Rust CI behavior checks. The OS metadata, Sysmon 15.22 executable/configuration, Hayabusa executable, selection JSON, fixture hashes and SYSTEM identity match the Go qualification inventory. Each campaign verifies the full 4,987-rule bundle and filter files; Hayabusa reports 2,269 enabled rules for the Sysmon EVTX input. All eight campaigns have healthy, complete captures.

Per-campaign evidence includes behavior output and exit status, executable hashes, exact-rule attribution, process GUIDs, manifests, inventories, capture health and raw-file hashes. Full EVTX/JSON/CSV, binaries, source snapshot, native CI logs, support bundle and SSM transcripts are archived under `/Users/michaellong/telemetry-lab-data/windows-rust-2026-09-22`. The shared `analyze.py` reproduces qualifications; nonzero exits for the two invalid `.onion` campaigns are intentional.

This completes the four-language composite implementations in PR #63. See [cross-platform scope](../../../../SCOPE.md). Paired tmon measurements, the final environment freeze and balanced repetitions remain #54; the broader executable/attribution and sensor audit remains #55.

The raw archive was downloaded and verified before lab teardown: SHA-256 `c287db2666c42dac0bce3ba10a17338adf90abf8cda16285e0ba6285bfae544b`. All 435 archived files match the locally retained captures and fixture logs. See `archive-manifest.json`. Final cleanup confirms zero temporary DNS policies, staged runtime DLLs or fixture servers, with the existing RDP listener still running (`cleanup.json`).
