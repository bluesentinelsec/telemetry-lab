# Windows C live qualification

Status: partial; network decisions remain pending. Twenty exact target rules were demonstrated in both UCRT and MSVCRT. All 44 same-binary controls passed. Across 88 CI-built attempts: 41 attributable target alerts, two valid misses (Public-folder path predicate), and one incomplete-attribution attempt. The last was retained alongside its successful recheck.

The same GCC 16.2.0 compiler version, fixed helper/module bytes, Sysmon/configuration, and Hayabusa artifact were used across the two CRT campaigns. Workflow artifact source: [run 35719860078](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/35719860078), commit `9cfab05`. All 24 program sources are unchanged since that build.

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
| tcp_connect_2525 | alert, alert | attribution-incomplete, alert |
| tcp_connect_3389 | not run | not run |
| tcp_connect_9389 | alert | alert |
| tcp_connect_88 | alert | alert |
| tcp_connect_public_path | valid-miss | valid-miss |
| dns_onion | not run | not run |
| dns_ip_lookup | not run | not run |
| double_extension_execute | alert | alert |
| creation_time_change | alert | alert |
| ads_executable | alert | alert |
| named_pipe_indicator | alert | alert |
| unsigned_node_load | alert | alert |

A successful recheck establishes a positive example; it does not erase the initial incomplete-attribution result or establish reliability. Sysmon emitted an SMTP-rule alert with a zero process GUID in the original MSVCRT attempt; the analyzer flags it instead of attributing it by PID alone or reporting a detector miss. The Public-folder rule missed in both CRTs because the otherwise attributed connection event had `Image=<unknown process>`. No causal CRT effect is established.

Per-campaign folders retain behavior output, exact-rule outcomes, identities, artifact manifests, health checks, and raw-file hashes. Full EVTX/JSON/CSV and initial development failures are locally archived under `/Users/michaellong/telemetry-lab-data/windows-c-2026-09-22`. The separate cross-compiled pilot is excluded from the 88-attempt CI-built summary.
