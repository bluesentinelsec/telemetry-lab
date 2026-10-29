# Windows C++ live qualification

Both libstdc++ and libc++ demonstrated the same **23 exact target rules out of 2,269 enabled Sysmon rules**, with clean same-binary controls. All 24 C reference cases are implemented as standalone C++ programs. The inherited `.onion` candidate remains unqualified in both libraries.

Artifacts: [CI run 35770862507](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/35770862507), source commit `b650f8b115b95a8d21e03f32dbf486ccbfa6b980`. Both builds use Clang 22.1.8 and UCRT; GNU libstdc++ and LLVM libc++ vary. All 24 binaries passed case-marker, unique-hash and library/CRT import checks. CI independently passed 17 non-network behaviors and 17 controls per library. Later evidence/documentation commits do not change those measured sources or the runner.

## Outcomes

| Campaign group | Attributable target alerts | Clean controls | Other outcomes |
|---|---:|---:|---|
| libstdc++: 17 non-network, five TCP, one DNS | 23 | 23 | None |
| libc++: same 23 cases | 22 | 23 | One DNS attribution failure |
| Reversed-order DNS recheck, both libraries | 2 | 2 | None |
| `.onion` diagnostic, both libraries | 0 qualified | 2 | Two failed-behavior attempts |
| **Total** | **47** | **50** | **One attribution failure; two invalid attempts** |

There were no valid target misses or failed controls. These 100 executions establish pilot qualification, not repeated-experiment reliability or equivalence of telemetry volume/composition.

The first libc++ `dns_ip_lookup` resolved to the expected 127.0.0.42 and generated its target-rule alert, but Sysmon record **210146** has a zero ProcessGuid and `<unknown process>` image. The analyzer classifies that attempt as `attribution-incomplete`, never a positive credited by PID. A reversed-order recheck with unchanged executables produced properly attributable DNS alerts in both libraries. The original failure is retained. This observation does not establish a causal C++ runtime effect.

Both `dns_onion` programs fail their unchanged successful-resolution check, matching the C limitation. The DNS-query rule can still alert on a rejected lookup, but that does not qualify the current positive behavior contract. No policy bypass, alternate resolver, or weakened assertion was introduced.

## Runtime, fixture and ruleset evidence

- The OS version, Sysmon binary/configuration, Hayabusa executable, helper/module hashes and execution identity match the C reference follow-up. The selection JSON changed only qualification-status metadata after that C campaign; the behavior contracts, target IDs and pinned rule inventory remain identical.
- The fixed C helper/module/echo/DNS fixtures come from reference CI run 35729429141, commit `a712ce984b147e76aeb8aa30edf95234b8409e7b`. The C++ campaigns use the same helper and module, ports, payload bytes, paths and five-second TCP lifetime. No C++ fixture rebuild is substituted into the comparison.
- All 4,987 supplied rule hashes and filter configurations are verified by the runner before each campaign. Hayabusa 4.1.0 reports 2,269 enabled Sysmon rules. Exact target IDs are joined to event record IDs and measured process GUIDs; setup, cleanup and server alerts do not count.
- [Loaded runtime evidence](loaded-runtime-evidence.json) verifies matching Sysmon EID 7 paths and SHA-256 hashes for every required bundled DLL in **all 100 measured executions**, with no opposite C++ library loaded. Both configurations use the same libgcc and winpthread DLL hashes; their C++ library DLL differs. The reproducible [verification script](verify-loaded-runtime.py) accepts the raw archive directory.
- Temporary DNS policies, staged runtime DLLs and fixture server processes were absent at final cleanup; the existing RDP listener remained active. See [cleanup.json](cleanup.json).

## Retention and reproduction

Per-campaign folders retain attempts (including behavior stdout/stderr), process identities, exact-rule outcomes, build manifests, inventory, capture health, detector logs and raw-file hashes. Fixture folders retain server logs and before/after DNS policy snapshots. `summary.json` contains the aggregate counts and CI artifact hashes.

Full EVTX/JSON/CSV captures, CI binaries and logs, support scripts and SSM transcripts are archived at `/Users/michaellong/telemetry-lab-data/windows-cpp-2026-09-22`. The raw archive was downloaded and SHA-256 verified against the Windows-created manifest before lab teardown; see [archive-manifest.json](archive-manifest.json). The C reference evidence remains unchanged.

Run the shared `analyze.py` on each raw campaign, then `verify-loaded-runtime.py` on the archive root. The analyzer intentionally returns nonzero for the first libc++ DNS campaign and both `.onion` diagnostics. Do not discard or replace those results with the successful recheck.

Windows Go and Rust ports, the `.onion` contract decision, paired tmon measurements and full repetitions remain tracked in #59 and #54. Sensor attribution reliability remains relevant to #55.
