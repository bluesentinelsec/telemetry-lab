# Windows C live qualification

**23 of 24 candidate targets demonstrated in both UCRT and MSVCRT.** The remaining `.onion` behavior contract awaits a user decision. The follow-up campaigns contain 100 attempts: 48 attributable target alerts, 50 clean controls, one incomplete-attribution attempt, and one failed-behavior attempt.

CI artifact source: [run 35729429141](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/35729429141), commit `a712ce984b147e76aeb8aa30edf95234b8409e7b`. Both builds use GCC 16.2.0, verified CRT imports, and the same fixed helper/module bytes. Every measured C source is unchanged since that build. Sysmon/configuration and the pinned Hayabusa 4.1.0 bundle are held constant across the paired CRT campaigns. Hayabusa reports 2,269 enabled Sysmon rules.

| Case | UCRT active outcomes | MSVCRT active outcomes |
|---|---|---|
| registry_run_key | alert | alert |
| registry_app_paths | alert | alert |
| registry_active_setup | alert | alert |
| registry_screensaver | alert | alert |
| registry_runmru_delete | alert | alert |
| startup_file | alert | alert |
| powershell_profile | alert | alert |
| public_binary | alert | alert |
| double_extension_file | alert | alert |
| double_extension_lnk | alert | alert |
| office_startup_file | alert | alert |
| suspicious_executable_file | alert | alert |
| tcp_connect_2525 | alert | alert |
| tcp_connect_3389 | alert | alert |
| tcp_connect_9389 | alert | alert |
| tcp_connect_88 | attribution-incomplete, alert | alert, alert |
| tcp_connect_public_path | alert | alert |
| dns_onion | invalid | not run |
| dns_ip_lookup | alert, alert | alert |
| double_extension_execute | alert | alert |
| creation_time_change | alert | alert |
| ads_executable | alert | alert |
| named_pipe_indicator | alert | alert |
| unsigned_node_load | alert | alert |

## Observations and limits

- All 17 non-network targets, five TCP targets, and the IP-lookup DNS target have positive examples and clean controls in both CRTs. RDP uses the existing listener; the four other TCP cases use localhost echo fixtures. Every TCP case and control holds the process alive for five seconds. Recorded TCP attempt durations are at least five seconds.
- Public-folder and RDP connection events now retain the required image path and alert. The earlier immediate-exit Public-folder misses remain in the initial evidence. This before/after observation does not by itself isolate process lifetime as the cause.
- The first follow-up UCRT port-88 event carries the probe PID but an older conhost.exe GUID/image. The rule alerts on that record, but it cannot be credited to the measured process. The analyzer flags conflicting identity as incomplete attribution. A reversed-order recheck with unchanged binaries produced attributable port-88 alerts in both CRTs; it does not erase the original problem or establish reliability.
- Windows rejects lab.onion with WSAHOST_NOT_FOUND (11001) before the local responder receives it. Sysmon records QueryStatus 9003 and the exact .onion rule alerts. Because the current program requires successful resolution, that active attempt is invalid, not a qualified positive. Reframing it as an attempted lookup with expected rejection requires the user decision requested during this follow-up. No .onion bypass or resolver-policy weakening was applied.
- api.ipify.org resolves to 127.0.0.42 through the local responder. Logs record the A queries; before/after NRPT snapshots show the temporary exact-name policies were removed. Adapter DNS settings and RDP service configuration remain unchanged.
- These are qualification observations, not the repeated dissertation experiment. No causal CRT-induced alert difference is established.

## Retained initial qualification

`initial-summary.json` preserves the preceding 88 CI-built attempts: 41 target alerts, 44 clean controls, two Public-folder misses and one incomplete-attribution attempt. Those campaign folders remain unchanged. The stricter analyzer was checked against all 88 original outcomes and leaves their classifications unchanged. The separate cross-compiled development pilots are excluded from both counts.

Per-campaign folders retain behavior output, exact-rule outcomes, process identities, artifact manifests, capture-health checks and raw-file hashes. Full EVTX/JSON/CSV, fixture logs, initial failures, and both sets of CI artifacts are archived locally under `/Users/michaellong/telemetry-lab-data/windows-c-2026-09-22`. Qualification JSON files are derived locally from the archived raw captures.
