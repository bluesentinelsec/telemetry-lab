# Windows C implementation and qualification

PR #60 implements 24 separate C executables for the candidate scope, built with GCC 16.2.0 in UCRT and MSVCRT configurations. The actual PE import tables establish the intended CRT; compiler versions and executable hashes are recorded in `build-manifest.json`. CI runs the 17 non-network behaviors and each same-binary control on both Windows configurations.

**23 exact targets are demonstrated in both C configurations.** The `.onion` candidate is implemented but its behavior contract remains unresolved. All other approved network fixture changes have been exercised in the lab.

## Live results

The follow-up Windows Server 2025 campaigns used the pinned Hayabusa 4.1.0 bundle and recorded Sysmon/configuration hashes. The engine reports **2,269 enabled Sysmon rules**. Across 100 attempts: 48 attributable target alerts, 50 clean controls, one conflicting-identity attempt and one failed lookup. See `validation/README.md` for the complete matrix and retained initial results.

- All 17 non-network targets alert in both CRTs with clean controls.
- All five TCP targets now have positive examples in both CRTs, including the existing RDP listener and Public-folder path rule. Every TCP program and control uses the same five-second lifetime hold.
- One UCRT port-88 connection was logged with the probe PID but an older conhost.exe GUID/image. The analyzer flags this as incomplete attribution; the unchanged case alerted correctly in both CRTs on a reversed-order recheck. Keep both observations.
- The IP-lookup DNS target alerts in both CRTs; the local responder logs the query and returns the fixed 127.0.0.42 answer. Temporary exact-name NRPT entries are removed afterward.
- Windows rejects `lab.onion` before contacting the local responder. Sysmon still records the attempted query and Hayabusa raises the target alert, but the program's successful-resolution check fails. That run is invalid under the current contract. The user has been asked whether to verify the attempted lookup and expected rejection or defer this case; neither choice has been assumed.

The preceding 88 attempts, including two Public-folder misses and one zero-GUID attribution problem, remain preserved separately. No causal runtime-induced alert difference is established by these qualification runs.

## Approved network fixture contract

The user approved all three fixture decisions on 2026-09-22:

1. Reuse the existing RDP listener. The 3389 program verifies connect and complete send of a fixed 11-byte X.224 request, then closes; it performs no authentication or session setup. No RDP service configuration changes are needed.
2. Use a local DNS responder with temporary exact-name NRPT policies for `lab.onion` and `api.ipify.org`. The responder returns 127.0.0.42 with zero TTL, records requests, and the harness removes its policies and clears cache afterward. Windows prevents the .onion query from reaching it; that unresolved case is documented above. It does not change adapter DNS servers or forward requests externally. The measured programs use ordinary `getaddrinfo`.
3. Hold each TCP client alive for five seconds after I/O, with the same hold in each no-I/O control. This is a fixed part of the cross-language behavior contract. It must not be selectively enabled only for cases or runtimes that miss.

Earlier immediate-exit attempts remain in `validation/`; new campaigns evaluate the approved fixtures separately.

## Reproduce

Build on Windows with the matching MSYS2 environment:

```sh
cmake -S ttp-composite/windows/c -B build-windows-c -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build-windows-c
cmake --install build-windows-c --prefix composite-dist/windows-c-ucrt
python ttp-composite/windows/coverage/verify_programs.py composite-dist/windows-c-ucrt/coverage ucrt
```

Repeat with MINGW64/MSVCRT and the corresponding output/config argument. Do not build one program containing multiple cases. The legacy four composites remain separate from the new `coverage/` suite and are not counted as newly qualified targets.

Use `-c windowsOnly=true -c stackName=WindowsCValidation` with the existing CDK app to deploy a disposable Windows-only lab. The runner verifies the Hayabusa executable, all inventoried rule files, and default exclusion/noisy files against the selected snapshot; a changed latest-release deployment must be restaged to the selected artifact rather than silently accepted.

Stage one fixed helper and unsigned module from the UCRT build as `C:\lab\windows-coverage\fixtures\helper.exe` and `fixture.node` for both CRT campaigns. The helper and module are benign fixtures, not measured language variants. The runner creates the remaining fixed document/shortcut/text fixtures and verifies file/registry behavior in the measured program. Use the same paths, filenames, helper bytes, and case mapping across subsequent languages.

```powershell
# Default: 17 non-network cases, each with a same-binary control.
.\run.ps1 -Programs C:\lab\ci-ucrt\coverage -Output C:\lab\qualification\ucrt-nonnetwork-01

# Five TCP cases: four echo fixtures plus the existing RDP listener.
.\run-local-tcp.ps1 -Programs C:\lab\ci-ucrt\coverage `
  -Output C:\lab\qualification\ucrt-tcp-01 `
  -EchoServer C:\lab\ci-ucrt\coverage\fixtures\windows_echo_server.exe

# Qualified resolver case; omit -Cases only after resolving the .onion contract.
.\run-local-dns.ps1 -Programs C:\lab\ci-ucrt\coverage `
  -Output C:\lab\qualification\ucrt-dns-01 `
  -Cases dns_ip_lookup `
  -DnsServer C:\lab\ci-ucrt\coverage\fixtures\windows_dns_server.exe
```

Each output directory must be new; old attempts are retained. `run.ps1` holds an exclusive machine-wide run mutex. The runner uses a fresh dedicated host and refuses unexpected pre-existing fixture files/RunMRU history; registry values it temporarily sets are restored. Run qualification sequentially and archive evidence before destroying the stack.

Analyze on a host with Python:

```sh
python analyze.py /path/to/campaign
```

The analyzer joins rule IDs to event record IDs and process GUIDs, including measured descendants. It never credits setup/cleanup or unrelated server activity. Missing process starts, run errors, overwritten logs, reported Sysmon errors/config changes, and incomplete GUID attribution are separated from valid misses. These checks do not prove lossless telemetry collection. The CLI returns nonzero for incomplete attribution, invalid attempts, failed controls, or target misses while preserving their results.

`-BehaviorOnly` is used by CI and does not establish alert coverage. This PR qualifies detection behavior; paired tmon event-volume/composition integration and full experiment repetitions remain tracked in #54.

## Evidence

See `validation/` for compact per-attempt qualifications, provenance, and hashes linking to locally archived raw campaigns. Full raw data and both CI artifact bundles are archived under `/Users/michaellong/telemetry-lab-data/windows-c-2026-09-22`. Initial development failures are preserved separately from the CI-built qualification campaigns; they are not silently treated as passing runs.
