# Windows C implementation and qualification

PR #60 implements 24 separate C executables for the candidate scope, built with GCC 16.2.0 in UCRT and MSVCRT configurations. The actual PE import tables establish the intended CRT; compiler versions and executable hashes are recorded in `build-manifest.json`. CI runs the 17 non-network behaviors and each same-binary control on both Windows configurations.

**The onboarding is not complete.** Twenty target rules have been demonstrated with attributable alerts and clean controls in both C configurations. The Public-folder TCP case misses its rule, and the RDP and two DNS fixtures remain pending user decisions. No claim is made that all 24 candidates alert.

## Live results

The live Windows Server 2025 host used Sysmon and the exact Hayabusa 4.1.0 bundle recorded in `selection.json`. The full pinned ruleset was evaluated with `dfir-timeline -m low --no-wizard`; the engine reports **2,269 rules enabled after the Sysmon channel filter**. Each campaign preserves the full EVTX, structured event fields, all detector alerts, behavior output, binary/fixture hashes, and process identities.

- All 17 non-network cases: exact target alert in both UCRT and MSVCRT; all 34 associated controls clean.
- TCP ports 88 and 9389: exact target alert and clean control in both CRTs using a separate localhost echo fixture.
- TCP port 2525: UCRT alerted with full attribution; the initial MSVCRT attempt emitted an alerting network event with a zero process GUID. That attempt is **attribution-incomplete**, not a valid miss. A targeted recheck in reversed CRT order produced attributable alerts and clean controls in both CRTs. Keep the initial incomplete attempt in the evidence.
- Public-folder TCP: the byte exchange and process identity checks pass, but both CRTs emit EID 3 with `Image=<unknown process>`. The path predicate does not match. This remains a valid no-alert observation under the recorded capture-health checks, not a qualified positive baseline. It is not established as a CRT-induced difference.
- RDP/3389 and two DNS cases: not lab-qualified. The current RDP executable expects echo semantics and must not be run against the existing RDP service as though it were an echo listener.

There is no established runtime-induced alert difference in this qualification. The short-lived TCP processes expose asynchronous sensor attribution limitations. Do not remove those attempts or count PID-only associations as successful target-rule attribution.

## Pending network decisions (requested from the user)

1. RDP occupies port 3389: use the existing listener with connect-and-send behavior, or temporarily stop RDP and use the echo fixture. No service changes have been made.
2. DNS: approve a local responder and temporary resolver configuration, or defer the two DNS tests. No DNS configuration has been changed.
3. Process lifetime: test a fixed five-second post-I/O pause in all TCP implementations and controls, or retain immediate exit and defer the path-based rule. No pause has been added.

The 24-rule selection is a candidate ledger, not a finalized experiment matrix. Freeze the qualified set only after these decisions and any required requalification.

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

# Four currently available TCP fixtures; does not touch RDP or DNS.
.\run-local-tcp.ps1 -Programs C:\lab\ci-ucrt\coverage `
  -Output C:\lab\qualification\ucrt-tcp-01 `
  -EchoServer C:\lab\ci-ucrt\coverage\fixtures\windows_echo_server.exe
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
