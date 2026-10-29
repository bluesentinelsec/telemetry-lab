# Windows Go live qualification

Both cgo and pure Go demonstrated the same **23 exact target rules out of 2,269 enabled Sysmon rules**, with clean same-binary controls. All 24 C/C++ cases are implemented as standalone Go programs. The inherited `.onion` candidate remains unqualified in both configurations.

Artifacts: [CI run 35779833371](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/35779833371), source commit `ee4518d`. Both builds use Go 1.23.12 and x/sys v0.24.0. The cgo configuration explicitly links runtime/cgo through GCC 16.2.0/UCRT; the pure-Go configuration omits cgo and directly imports only kernel32.dll. The measured behaviors remain in Go/Windows bindings. CI checks build metadata, actual cgo symbols, PE imports, each binary's sole case marker and unique hash. Both configurations passed 17 non-network behaviors and 17 controls in CI.

The follow-up runner is commit `76ab32b9a60f5d18dd1de165ff5ff573b3daf19c`, SHA-256 `e4afafd2e054639fa7ba1a1cb2c19b49748062db9793c4da6a4666f39ec99746`. The follow-up uses the **unchanged CI-built executables** from the initial campaigns; only harness verification/cleanup changed. Both support ZIPs and SSM scripts are archived.

## Complete qualification

The six non-network/TCP/ordinary-DNS `-02` campaigns contain **92 executions: 46 attributable target alerts and 46 clean controls**, with no target misses, attribution failures or invalid attempts. This covers all 17 non-network targets, all five TCP targets, and `dns_ip_lookup` in both configurations. The exact rule IDs, paths, fixture contents, ports, payloads and five-second TCP lifetime match C/C++.

An exploratory comparison of all attributable rule-ID alert counts in those paired active/control runs also found no differences between Go configurations. See `secondary-alert-comparison.json`. These incidental alerts do not expand the 23-rule qualified numerator, and single qualification runs do not establish repeated-experiment reliability or a causal runtime effect.

## `.onion` and complete accounting

Both `.onion` active attempts fail the unchanged successful-resolution requirement; their controls pass. These two active attempts are invalid rather than qualified positives, even if the attempted query produces an alert. No custom resolver, new endpoint or weakened behavior contract was introduced.

Across all retained campaigns there are **141 recorded executions: 68 target alerts, 70 clean controls and three invalid attempts**, with no valid misses, failed controls or incomplete GUID attributions. The three invalid attempts comprise the initial DNS control in its aborted campaign and the two `.onion` active failures. There were 188 planned invocations; 47 were never launched because of the retained initial harness failures. The complete follow-up is the 92-execution qualification cohort above; the additional four `.onion` invocations are diagnostic.

## Retained initial harness failures

The initial cgo non-network and TCP campaigns produced 22 target alerts and 22 clean controls. During the initial DNS campaign, the control completed successfully but removal of its image failed with a sharing violation. That campaign stopped before its active case, so its one recorded attempt is invalid under the complete-campaign contract. The leftover file then blocked all three initial pure-Go campaigns before launch. Those directories retain their errors, capture health and planned/recorded counts; a zero-attempt campaign is never treated as a passing test.

The known leftover image was hash-checked against the archived cgo DNS binary before removal, with no active measured process. The shared runner now retries removal of owned files for up to five seconds after process exit, records any retries, and still fails on persistent errors. This changes harness cleanup, not the measured process lifetime or positive behavior. The full follow-up completed without those campaign failures.

## Sysmon image-hash observations

Sysmon sometimes repeats an earlier executable's hash after the same neutral image path is reused. For example, initial `registry_app_paths` record 215052 reports the preceding `registry_run_key` hash, while the app-paths program emits its own fixed case marker and passes its independent behavior check. The same kind of discrepancy persists in the follow-up even when the staged file is independently hash-verified before launch. The precise sensor/cache mechanism has not been isolated.

The runner now reads the SHA-256 of the copied `probe.exe` immediately before each launch and refuses a mismatch with the CI manifest. This measurement occurs in the harness, outside the measured process. Sysmon's reported hash is preserved unchanged; it does not replace the staged-file check. Alerts remain joined through their exact rule ID, event record and measured process GUID, including only the explicitly allowed child. The selected target predicates do not depend on image hashes.

All 96 follow-up/diagnostic launches have matching staged and CI manifest hashes. Sysmon image hashes differ from the expected binary in 124 of all 141 retained executions (including the initial campaigns); those observations remain visible rather than being rewritten. `runtime-evidence.json` records each expected/staged/Sysmon hash, process-start record and UCRT load observation. `verify-runtime.py` reproduces that audit from the raw campaign directories. A pure-Go process may load system libraries indirectly through Windows APIs; the build checks establish absence of cgo and direct C-runtime imports, not absence of every possible C-based system DLL. The initial campaigns lack the new staged-hash field and are identified separately.

## Collection and provenance

The OS version, Sysmon executable/configuration, Hayabusa executable, execution identity, selection JSON and fixed helper/module hashes match the C++ reference. Live fixtures come from C reference CI run 35729429141: no Go-specific helper/server is substituted. All 4,987 bundled rule hashes and filter configurations are verified before each campaign; Hayabusa 4.1.0 reports 2,269 enabled Sysmon rules.

The PE verifier parses the on-disk import directory directly. GNU objdump misinterpreted the import table in the internally linked Go binaries with compressed debug sections and printed no DLL names; that was corrected before live qualification. The replacement is checked against actual C/C++ import lists and rejects malformed/empty tables. Initial build artifacts are archived separately from the correctly verified live artifacts.

Per-campaign folders retain behavior stdout/stderr, process identities, exact-rule outcomes, manifests, inventory, health checks, detector logs, errors and raw-file hashes. Fixture folders retain server logs and DNS policy snapshots. Full EVTX/JSON/CSV, binaries, CI logs, support bundles and SSM scripts are archived at `/Users/michaellong/telemetry-lab-data/windows-go-2026-09-22`. Derived qualifications are reproduced with the shared `analyze.py`; nonzero results for incomplete/invalid campaigns are intentional. The C and C++ evidence remains unchanged.

Windows Rust, the final `.onion` contract decision, paired tmon measurements and full repetitions remain #59/#54. The observed Sysmon metadata issue remains relevant to #55 when freezing the full experiment.

The raw archive was downloaded and SHA-256 verified against the Windows-created manifest before lab teardown; its hash is `8b69d5a1496a2ea42fed18e896a8e714fa5c45be4c726e3bebca4f1ca96fa703`. EVTX/JSON/CSV/plan contents for every campaign also match the archived local files. See `archive-manifest.json`. Final cleanup confirms no temporary DNS policy, owned runtime DLLs or fixture servers remain, with RDP still listening (`cleanup.json`).
