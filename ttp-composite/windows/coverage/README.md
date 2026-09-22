# Windows TTP composite rule selection

**Status: proposed scope; 24 candidates, zero newly lab-qualified tests.**

The Windows pipeline collects Sysmon events into EVTX and evaluates them with Hayabusa. The subject is the unmodified rule bundle shipped in the Hayabusa 4.1.0 Windows x64 release, not the entire upstream Sigma repository. All 24 selected rules are Sigma-derived Sysmon rules.

## Rule-count denominator

| Scope | Unique rule IDs |
|---|---:|
| All supplied rule definitions | 4,987 |
| Definitions referencing the Sysmon Operational channel | 2,455 |
| Sysmon definitions passing the static scope filters below | 2,269 |
| Proposed target rules | 24 |
| Newly lab-qualified target rules | 0 |

Static filters follow the existing `-m low --no-wizard` configuration: remove informational, deprecated, unsupported, default excluded/noisy IDs, and rules with unresolved expansion placeholders. Overlapping exclusions are counted once. Channel membership means the detection references Sysmon, not that every rule can be satisfied using Sysmon alone. This inventory is not an engine-load or lab-coverage result; rule compilation, channel dependencies, and actual event capture must be confirmed before freezing the final denominator.

Proposed scope statement: "We will develop 24 Windows composite tests against 24 selected rules from 2,455 Sysmon-referencing definitions in the pinned Hayabusa bundle." After engine verification and C qualification, report the qualified numerator and configured denominator separately.

## Selection rationale

Choose directly reproducible operations with specific event predicates, equivalents in all four languages, independent behavior checks, and controllable fixtures. Avoid building the scope from wrappers around PowerShell or reg.exe, since those would mainly measure a common child tool. Include path/name-based rules where the program must actually create, execute, load, or resolve the matching artifact; label those limits explicitly. The 24 targets span nine behavior families. Their predicates reference 12 event IDs; an individual case may exercise only one of a rule's permitted event IDs.

## Proposed cases

Network scope refined on 2026-09-22: see [network-scope.md](network-scope.md). Seven network/DNS candidates use basic TCP I/O or ordinary hostname resolution; the LDAP-discovery candidate is deferred.

| Standalone case | Exact bundled rule title | Sysmon event IDs |
|---|---|---|
| `registry_run_key` | CurrentVersion Autorun Keys Modification | 13 |
| `registry_app_paths` | Potential Persistence Via App Paths Default Property | 13 |
| `registry_active_setup` | Run Once Task Configuration in Registry | 12, 13, 14 |
| `registry_screensaver` | Path To Screensaver Binary Modified | 12, 13, 14 |
| `registry_runmru_delete` | RunMRU Registry Key Deletion - Registry | 12 |
| `startup_file` | Startup Folder File Write | 11 |
| `powershell_profile` | PowerShell Profile Modification | 11 |
| `public_binary` | Suspicious Binaries and Scripts in Public Folder | 11 |
| `double_extension_file` | Suspicious Double Extension Files | 11 |
| `double_extension_lnk` | Suspicious LNK Double Extension File Created | 11 |
| `office_startup_file` | Potential Persistence Via Microsoft Office Startup Folder | 11 |
| `suspicious_executable_file` | Suspicious Executable File Creation | 11 |
| `tcp_connect_2525` | Suspicious Outbound SMTP Connections | 3 |
| `tcp_connect_3389` | Outbound RDP Connections Over Non-Standard Tools | 3 |
| `tcp_connect_9389` | Uncommon Connection to Active Directory Web Services | 3 |
| `tcp_connect_88` | Uncommon Outbound Kerberos Connection | 3 |
| `tcp_connect_public_path` | Network Connection Initiated From Process Located In Potentially Suspicious Or Uncommon Location | 3 |
| `dns_onion` | DNS Query Tor .Onion Address - Sysmon | 22 |
| `dns_ip_lookup` | Suspicious DNS Query for IP Lookup Service APIs | 22 |
| `double_extension_execute` | Suspicious Double Extension File Execution | 1 |
| `creation_time_change` | File Creation Date Changed to Another Year | 2 |
| `ads_executable` | Hidden Executable In NTFS Alternate Data Stream | 15 |
| `named_pipe_indicator` | Malicious Named Pipe Created | 17, 18 |
| `unsigned_node_load` | Unsigned .node File Loaded | 7 |

## Qualification contract

1. Pin the Windows image, Sysmon executable/configuration, Hayabusa executable, rule bytes, and execution identity before qualifying C. The deployment currently follows latest releases; the archived pilot used Hayabusa 3.10.0, whereas this proposal inventories 4.1.0. These scopes must not be combined.
2. Implement each case as its own executable, with a same-binary no-behavior control. Hold path, filename, arguments, destination, payload bytes, and helper programs constant across C, C++, Go, and Rust. A control is allowed; a multi-case dispatcher is not.
3. Prove behavior independently of alerts: file/registry readback, helper result, listener receipt, DNS observation, pipe exchange, or timestamp readback. Distinguish unsuccessful behavior from successful behavior without an alert.
4. Require a positive exact-rule alert for the C reference implementation and no attributable target-rule alert in its no-behavior control. Associate alert records with process GUIDs, descendants when applicable, record IDs, and bounded capture windows; retain EVTX and detector output. Setup and cleanup must not masquerade as the measured action.
5. Replay the full pinned eligible bundle and score the predetermined target IDs. Preserve other alerts as secondary observations, without counting them as successful coverage of the intended rule.
6. Port the same behavior and target IDs in order C, C++, Go, Rust, one feature PR per language. Keep genuine misses in later configurations as results when the behavior and capture checks pass; investigate field/event differences before attributing a miss to runtime.
7. Freeze the qualified scope before the full experiment. Record rejected candidates and reasons; do not silently swap rules by language. C qualification selects for behavior detectable in the C baseline, so conclusions must acknowledge that sampling choice.

## Fixture details and exact rule identities

### registry_run_key: CurrentVersion Autorun Keys Modification

- Bundled rule ID: `3f59aeed-e4fb-6b21-a7fa-a327fdb8494d`.
- File: `sigma/sysmon/registry/registry_set/registry_set_asep_reg_keys_modification_currentversion.yml`.
- Behavior: Write a nonempty HKCU Run value pointing to a fixed benign helper; read it back and remove it before any logon.
- Conditions: Use an unused fixture value under the actual Run key; preserve any pre-existing data. Control writes to an ordinary fixture key.

### registry_app_paths: Potential Persistence Via App Paths Default Property

- Bundled rule ID: `140df4ae-d66c-c984-2165-595d754d0424`.
- File: `sigma/sysmon/registry/registry_set/registry_set_persistence_app_paths.yml`.
- Behavior: Set the default App Paths value for an unused helper name to a benign helper under C:\Users\Public; read back and restore.
- Conditions: Path must match a suspicious-location predicate. Do not replace an existing application registration.

### registry_active_setup: Run Once Task Configuration in Registry

- Bundled rule ID: `46f90542-f6e6-75d1-c29d-e26535273ec0`.
- File: `sigma/sysmon/registry/registry_event/registry_event_runonce_persistence.yml`.
- Behavior: Write and read back StubPath beneath a fresh Active Setup Installed Components GUID, then remove it.
- Conditions: Use an isolated user hive and inert helper command; no logon activation. This tests registration evidence, not completed persistence.

### registry_screensaver: Path To Screensaver Binary Modified

- Bundled rule ID: `ec1e8c56-2fa0-7417-e4b3-517d291e30b2`.
- File: `sigma/sysmon/registry/registry_event/registry_event_modify_screensaver_binary_path.yml`.
- Behavior: Set and read back the isolated test account SCRNSAVE.EXE value, then restore it.
- Conditions: Do not activate a screensaver; the native program must not have an excluded explorer.exe or rundll32.exe image name.

### registry_runmru_delete: RunMRU Registry Key Deletion - Registry

- Bundled rule ID: `ec2a6d71-1139-d6f1-c39e-e9fc35500540`.
- File: `sigma/sysmon/registry/registry_delete/registry_delete_runmru.yml`.
- Behavior: Delete a harness-seeded RunMRU fixture key in an isolated account; independently verify absence.
- Conditions: Seed outside the measured window and preserve prior state. The rule also matches creation events because it lacks an EventType filter; control must not create this key.

### startup_file: Startup Folder File Write

- Bundled rule ID: `daaf04a9-5b60-e331-6611-a3a32797e550`.
- File: `sigma/sysmon/file/file_event/file_event_win_startup_folder_file_write.yml`.
- Behavior: Write a fixed inert fixture file to the test account Windows Startup directory; verify bytes, then remove.
- Conditions: Use a real resolved Startup path. Qualification measures a startup-folder write, not whether a payload executes at logon.

### powershell_profile: PowerShell Profile Modification

- Bundled rule ID: `5d1e6a6b-91ca-c7e8-821c-5c665ad9ca5e`.
- File: `sigma/sysmon/file/file_event/file_event_win_susp_powershell_profile.yml`.
- Behavior: Create a comment-only Microsoft.PowerShell_profile.ps1 under the isolated test account profile; verify and remove.
- Conditions: Preserve any existing profile. No PowerShell child is needed to create the artifact.

### public_binary: Suspicious Binaries and Scripts in Public Folder

- Bundled rule ID: `ef4c38c9-e26f-dcfe-1cbe-6323bafb8f39`.
- File: `sigma/sysmon/file/file_event/file_event_win_susp_public_folder_extension.yml`.
- Behavior: Write the same benign PE fixture under C:\Users\Public; independently verify its hash.
- Conditions: Hold destination and fixture bytes constant across all language builds; remove after capture.

### double_extension_file: Suspicious Double Extension Files

- Bundled rule ID: `c69c8c8d-4188-72ea-ca61-a2a1a80612b3`.
- File: `sigma/sysmon/file/file_event/file_event_win_susp_double_extension.yml`.
- Behavior: Write a fixed benign PE fixture named report.pdf.exe; verify its hash without executing it.
- Conditions: File creation is the target operation; the measured program itself keeps a neutral name.

### double_extension_lnk: Suspicious LNK Double Extension File Created

- Bundled rule ID: `6b7cbf57-a67c-6e5a-61c6-4d92d02fff3e`.
- File: `sigma/sysmon/file/file_event/file_event_win_susp_lnk_double_extension.yml`.
- Behavior: Write a fixed valid benign shortcut fixture named report.pdf.lnk outside Recent folders; verify bytes.
- Conditions: Use the same prebuilt shortcut bytes in every language; do not launch it.

### office_startup_file: Potential Persistence Via Microsoft Office Startup Folder

- Bundled rule ID: `be512a1b-170e-acff-f35d-0e4b44caa2a3`.
- File: `sigma/sysmon/file/file_event/file_event_win_office_startup_persistence.yml`.
- Behavior: Write a fixed benign document fixture under the isolated profile Microsoft\Word\STARTUP directory; verify and remove.
- Conditions: The rule detects path and extension, not Office execution; Office need not be installed and persistence is not claimed.

### suspicious_executable_file: Suspicious Executable File Creation

- Bundled rule ID: `9512176f-0e9f-7f30-fa82-d414c1c80248`.
- File: `sigma/sysmon/file/file_event/file_event_win_susp_executable_creation.yml`.
- Behavior: Write a fixed benign PE fixture named lab.sys.exe; independently verify bytes.
- Conditions: This is a filename-based file-creation predicate, not evidence that a driver was installed.

### tcp_connect_2525: Suspicious Outbound SMTP Connections

- Bundled rule ID: `f8a59cdc-b3d1-8f59-c3f4-4db6d94e8efc`.
- File: `sigma/sysmon/network_connection/net_connection_win_susp_outbound_smtp_connections.yml`.
- Behavior: Use ordinary TCP sockets to connect to a lab-owned private peer on port 2525, send the fixed telemetry-lab marker, receive the fixed reply, and close. Verify the complete byte exchange at both ends.
- Conditions: Use the same neutral executable path/name and private IPv4 peer across languages, outside all process exclusions. No protocol handshake, client library, authentication, or real application service is required by the rule. Pin source/peer setup; validate actual Sysmon EID 3 attribution.

### tcp_connect_3389: Outbound RDP Connections Over Non-Standard Tools

- Bundled rule ID: `f3fa6209-076f-c860-c7cb-e2f6bdd7d3e0`.
- File: `sigma/sysmon/network_connection/net_connection_win_rdp_outbound_over_non_standard_tools.yml`.
- Behavior: Use ordinary TCP sockets to connect to a lab-owned private peer on port 3389, send the fixed telemetry-lab marker, receive the fixed reply, and close. Verify the complete byte exchange at both ends.
- Conditions: Use the same neutral executable path/name and private IPv4 peer across languages, outside all process exclusions. No protocol handshake, client library, authentication, or real application service is required by the rule. Pin source/peer setup; validate actual Sysmon EID 3 attribution.

### tcp_connect_9389: Uncommon Connection to Active Directory Web Services

- Bundled rule ID: `ae8c1c58-4743-c0c8-3b30-7d69f7cbee68`.
- File: `sigma/sysmon/network_connection/net_connection_win_adws_unusual_connection.yml`.
- Behavior: Use ordinary TCP sockets to connect to a lab-owned private peer on port 9389, send the fixed telemetry-lab marker, receive the fixed reply, and close. Verify the complete byte exchange at both ends.
- Conditions: Use the same neutral executable path/name and private IPv4 peer across languages, outside all process exclusions. No protocol handshake, client library, authentication, or real application service is required by the rule. Pin source/peer setup; validate actual Sysmon EID 3 attribution.

### tcp_connect_88: Uncommon Outbound Kerberos Connection

- Bundled rule ID: `322fd5f2-b5b7-1bf4-58f2-92873dc878bb`.
- File: `sigma/sysmon/network_connection/net_connection_win_susp_outbound_kerberos_connection.yml`.
- Behavior: Use ordinary TCP sockets to connect to a lab-owned private peer on port 88, send the fixed telemetry-lab marker, receive the fixed reply, and close. Verify the complete byte exchange at both ends.
- Conditions: Use the same neutral executable path/name and private IPv4 peer across languages, outside all process exclusions. No protocol handshake, client library, authentication, or real application service is required by the rule. Pin source/peer setup; validate actual Sysmon EID 3 attribution.

### tcp_connect_public_path: Network Connection Initiated From Process Located In Potentially Suspicious Or Uncommon Location

- Bundled rule ID: `df13f270-859b-272a-9c2a-a0ef744a0480`.
- File: `sigma/sysmon/network_connection/net_connection_win_susp_initiated_uncommon_or_suspicious_locations.yml`.
- Behavior: Execute the standalone program at C:\Users\Public\telemetry-lab\probe.exe and perform a TCP connect/send/receive exchange with a lab-owned private peer on fixed port 49152.
- Conditions: Hold the executable location constant across languages. Use a controlled destination hostname outside filter_main_domains. Stage the program before capture; observe the connection from the actual measured process, not a launcher. Confirm bytes received at both ends.

### dns_onion: DNS Query Tor .Onion Address - Sysmon

- Bundled rule ID: `29e2035f-b91f-3c35-9a7a-087b864f6d3b`.
- File: `sigma/sysmon/dns_query/dns_query_win_tor_onion_domain_query.yml`.
- Behavior: Resolve lab.onion using the normal language hostname-to-address resolver and an isolated lab DNS server supplying a fixed local answer.
- Conditions: No Tor client or public forwarding. Independently verify the lookup result and resolver request. Qualify C EID 22 attribution; if the resolver rejects the special-use name, resolve that fixture limitation before accepting this target. Establish the same DNS-cache baseline for each attempt.

### dns_ip_lookup: Suspicious DNS Query for IP Lookup Service APIs

- Bundled rule ID: `e1d5e512-66be-e3eb-e24b-a9f3545e115a`.
- File: `sigma/sysmon/dns_query/dns_query_win_susp_external_ip_lookup.yml`.
- Behavior: Resolve api.ipify.org against an isolated lab resolver that supplies a fixed local answer.
- Conditions: No HTTP client or public service contact. Preserve the hostname, answer, and DNS-cache baseline across languages; independently verify lookup results and resolver request. Keep the executable outside browser image exclusions.

### double_extension_execute: Suspicious Double Extension File Execution

- Bundled rule ID: `b6ce0b2f-593b-5e1c-e137-d30b2974e30e`.
- File: `sigma/sysmon/process_creation/proc_creation_win_susp_double_extension.yml`.
- Behavior: Launch a fixed benign report.pdf.exe helper with the same command line and verify its marker and exit code.
- Conditions: Both Image and CommandLine must match. Control uses the same parent program but does not spawn the matching child.

### creation_time_change: File Creation Date Changed to Another Year

- Bundled rule ID: `1117f7b2-3f59-682b-ad07-081d44ae5ddb`.
- File: `sigma/sysmon/threat-hunting/file/file_change/file_change_win_date_changed_to_another_year.yml`.
- Behavior: Change a harness-seeded file creation time from a fixed 2026 value to a fixed 2019 value; read the timestamp back.
- Conditions: This rule compares the 202 prefix, not any year change: 2026 to 2025 would not match. Avoid .tmp/.temp and excluded paths.

### ads_executable: Hidden Executable In NTFS Alternate Data Stream

- Bundled rule ID: `e5cca2eb-74d0-c45b-ec14-3c09f568f8c0`.
- File: `sigma/sysmon/create_stream_hash/create_stream_hash_ads_executable.yml`.
- Behavior: Write a fixed benign PE with a nonzero import hash to an NTFS alternate data stream and verify its bytes.
- Conditions: Requires Sysmon EID 15 and IMPHASH in Hash. Do not execute the stream; confirm capture and hash fields during qualification.

### named_pipe_indicator: Malicious Named Pipe Created

- Bundled rule ID: `cb1d1446-f327-1659-42ad-e41a7bc16e36`.
- File: `sigma/sysmon/pipe_created/pipe_created_susp_malicious_namedpipes.yml`.
- Behavior: Create the named pipe \testPipe, connect a controlled client and exchange a fixed marker.
- Conditions: This tests a listed pipe-name indicator; it does not emulate the malware families in the rule description. Keep client activity separately attributable.

### unsigned_node_load: Unsigned .node File Loaded

- Bundled rule ID: `8085fb71-ed3b-7920-ca06-f9174665cc8a`.
- File: `sigma/sysmon/image_load/image_load_dll_unsigned_node_load.yml`.
- Behavior: Load a fixed benign unsigned DLL fixture with a .node extension into the measured process; call a harmless exported function.
- Conditions: Same helper bytes in every language; verify load and function result. Requires EID 7 plus Signed=false or SignatureStatus=Unavailable; Node.js execution is not claimed.

## Deferred candidates and existing tests

- Callback and uncommon-port rules exclude loopback, RFC1918 and link-local addresses. Defer them until an isolated routed fixture can satisfy the unmodified destination predicate; do not call a localhost miss a runtime effect.
- Existing `reverse_shell`, `imds`, `registry_run_key`, and `startup_folder` programs are not automatically qualified against this bundle. Run-key and Startup behaviors have explicit targets above. The old reverse-shell command-process assumption and IMDS attempt need exact rule mapping and behavior evidence before reuse.
- Defer rules requiring Security audit events, PowerShell logs, Defender logs, Office execution, domain infrastructure, custom Sysmon RuleName values, or unavailable event classes. Those requirements would expand the current collection scope.
- Do not represent port-only connections, file-name indicators, DNS names, or persistence-location writes as full successful attacks. They reproduce the observable conditions the selected rules actually evaluate.
- The existing Windows build matrix covers C, C++, and Go configurations. Rust Windows toolchains/runtime configurations still need to be selected and validated; Linux GNU/musl configurations cannot simply be copied over.

## Provenance and reproducibility

[Official Windows release](https://github.com/Yamato-Security/hayabusa/releases/tag/v4.1.0). `selection.json` records exact candidate predicates, related upstream IDs, rule-file hashes, executable/archive hashes, and filter-file hashes. `rule-inventory.csv` records all 4,987 definitions and the static scope decisions.

The bundled rules repository reports HEAD `fffbdd179c8c8c7554368c443f9ba2917877f108`, while the Hayabusa release tag points its rules gitlink at `e9a98d49313eed67fe1a2c21c0b108e04fdebe66`. The release ZIP and per-file hashes are authoritative for this inventory; do not substitute the tag gitlink snapshot. No installed lab rules or deployment configuration have been changed.

## Resume decision: issue #59

Windows onboarding is tracked at https://github.com/bluesentinelsec/telemetry-lab/issues/59. The initial candidates are generally accepted, with a new constraint: network composites stay close to basic socket/DNS primitives, without SMTP, RDP, ADWS, Kerberos, or LDAP client libraries or protocol implementations. The four port-based rules may use simple connections to controlled listeners. Defer LDAP SRV discovery unless justified within the existing primitive-level scope without new dependencies. The final count remains TBD; the ledger above reflects the 2026-09-22 refinement, not a frozen implementation commitment. Resume with C, then C++, Go, and Rust in separate feature PRs.
