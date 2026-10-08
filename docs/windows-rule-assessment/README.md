# Windows composite expansion assessment

**Recommendation: qualify four additional Windows cases, with one conditional second wave.** Prioritize new behavior or predicate dimensions rather than a larger rule percentage. Keep the official scope at 52 qualified rules until new cases have independent behavior evidence, attributable alerts, and clean same-binary controls. Linux is outside this assessment.

This is a static assessment against repository revision `5011471`, dated October 8, 2026. No programs, rules, collector configurations, archived data, or slide files were changed. No lab was deployed. Candidate feasibility and expected alert behavior remain hypotheses pending native qualification.

**Review basis**

The local Hayabusa 4.1.0 archive matches the recorded SHA-256 `4d304cc5baaa750ed08cc24b7b89c58ea058740c7e344502d7b82554637543a8`. All 4,987 inventoried rule files matched their individual hashes and were parsed (4,993 YAML documents, including multi-document files). The existing full-corpus triage was examined by event IDs and predicate dependencies. Twenty-nine promising candidates, alternatives, and apparent event-family gaps received manual predicate/fixture review; their exact detection predicates, authors, source links, and decisions are preserved in [reviewed-candidates.json](reviewed-candidates.json). This is not a manual feasibility certification of all 2,269 eligible rules.

The full inventory still has 52 selected rules, 2,215 awaiting fixture review, one deferred after validation, and one explicitly excluded among the 2,269 eligible rules. Another 2,718 are outside the current detector profile. The earlier `.onion` exclusion and LDAP qualification failure remain intact.

**Where additional scope would help**

The current 52 targets contain 15 registry cases, 15 file-creation cases, nine network/DNS cases, four deletion cases, three named-pipe cases, and six other cases. Thirty of 52 therefore concern registry operations or file creation. There is only one primary process-creation case, one image-load case, and one stream-hash case.

The eligible corpus has 1,418 rules referencing process creation (62.5% of 2,269), 125 referencing image loading, 33 process access, 17 remote-thread creation, ten stream creation, and two raw reads. Event memberships overlap and must not be summed. Large counts do not imply many independent operations: application identity, command-line strings, paths, hashes, and indicators account for many variations.

The current selection has only one rule referencing `CommandLine` and no selected rule referencing `Contents` or `CallTrace`. This makes argument transport and stream-content predicates more useful additions than further file-extension, DNS-name, or registry-path variants. CallTrace deserves exploratory observation, but forcing a particular stack predicate would compromise the runtime comparison.

**Four candidates to qualify next**

| Priority | Proposed case and exact primary rule | Added dimension | Fixture and admission condition |
| --- | --- | --- | --- |
| 1 | `unicode_child_arguments` — Potential CommandLine Obfuscation Using Unicode Characters (`efe8a84a-0bef-c646-b13a-5a3cbe2b01b9`) | Unicode argument transport and command-line representation; Sysmon 1 | Launch the same benign helper with identical logical arguments containing a listed Unicode character. Verify the helper received the exact argument sequence. Freeze encoding and API semantics across implementations. The rule requires a listed character, not a malicious command. |
| 2 | `ads_provenance_contents` — Unusual File Download from Direct IP Address (`ecb9ed8e-9e96-85bd-a68e-c86d68005053`) | Text content in an alternate stream; Sysmon 15 `Contents` regex | Write fixed synthetic Zone.Identifier metadata containing a numeric-IP URL to an owned carrier with a matching extension; verify exact bytes. No download or external connection is required or claimed. Confirm the real captured Contents field and attribution. This differs from the existing ADS test's IMPHASH predicate. |
| 3 | `raw_owned_volume_read` — Potential Defense Evasion Via Raw Disk Access By Uncommon Tools (`f4ca1a32-116e-1b6b-6d74-233983928c00`) | Raw-volume I/O and a new selected event family, Sysmon 9 | Prepare a disposable owned virtual disk/volume before capture; read known bytes and verify them. Never use a real system/data volume as the fixture. Verify privileges, device naming, collector emission, and process GUID. Use a measured program location outside the rule's exclusions. Native API use may produce limited runtime variation; retain that outcome. |
| 4 | `signed_system_library_load` — Load Of RstrtMgr.DLL By An Uncommon Process (`1b615dd1-9d33-03df-fb06-d8fc0ee7d654`) | Genuine signed system-library loading, extending the current unsigned .node fixture; Sysmon 7 | Load the same genuine system RstrtMgr.dll without invoking Restart Manager actions. Freeze its hash and program location; verify the loaded module. Establish that controls neither preload it nor alert. This adds an artifact/load context, not a new event family; its incremental value is lower than the first three. |

All four are Sigma-derived and already eligible in the pinned evaluation inventory. No change to upstream predicates is proposed. RawAccessRead, ProcessCreate, FileCreateStreamHash, and ImageLoad are present in the current Sysmon profile; that configuration evidence does not substitute for live emission checks. Microsoft's descriptions distinguish raw reads, stream-content recording, and image loads: [Sysmon event documentation](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).

Implement behavior through each language's normal facilities where available, documenting native Windows API fallbacks. Identical Win32 calls may reduce the opportunity for runtime-specific differences. Do not claim that these additions are guaranteed to produce alert differences, and do not change the behavior or encoding by runtime to make them do so.

If all four qualify, scope becomes **56 target rules × eight configurations**. Four new active/control cases at 200 repetitions add **12,800 executions**, increasing Windows composite execution count by 7.7%, from 166,400 to 179,200, before replacements. Rule coverage moves from 2.29% to 2.47% of the eligible corpus; the rationale is the added dimensions, not that small percentage increase. Only the raw-read case necessarily adds a new cataloged behavior family.

**One conditional second wave**

`remote_library_thread` could target **CreateRemoteThread API and LoadLibrary** (`fedc7a8c-ccbd-62df-314a-7aeaa18aa325`). Its predicates require `StartModule` ending in kernel32.dll and `StartFunction` exactly LoadLibraryA. The current remote-thread case instead centers on target-process identity. A benign owned-helper/library fixture could add start-function/module sensitivity, but export forwarding, actual sensor symbol attribution, cleanup, and implementation complexity need a C feasibility pilot first. Do not weaken the predicate, force reported symbols, or substitute a different mechanism for each runtime. Admit only if it adds usable evidence within the schedule. A fifth case adds another 3,200 executions at the stated allocation.

**Candidates to defer or keep as secondary observations**

| Candidate group | Assessment |
| --- | --- |
| WMI filter/consumer/binding named alerts | The three Hayabusa-native rules require `RuleName` other than empty or `-`. The current broad collection profile does not define named WMI predicates. The current analyzer joins events by measured/descendant process GUID; WMI object registration needs a separately validated ownership strategy. |
| WMI script/encoded consumer rules | Two Sigma rules use `Destination` predicates without requiring RuleName. These are a meaningful future COM/WMI family, but an inert, unbound consumer fixture needs object readback, ownership, cleanup, and attribution beyond the present process join. They are not declared impossible. |
| Clipboard | The eligible Hayabusa-native target also requires a nonempty named Sysmon rule. Session/clipboard fixtures and a changed profile would be needed; it is not an immediate case under the current design. |
| Executable-file detection, Sysmon 29 | Eligible rules exist, but `FileExecutableDetected` is not explicitly configured in the current profile. Verify live enablement before assuming it is available. Any profile change must be frozen and assessed across the suite. Existing benign PE-write fixtures may exercise it without a new behavior case. |
| Blocking events, Sysmon 27/28 | These represent prevented operations rather than the present passive measurement profile; they would change the success/control interpretation. Defer as a separate design. |
| Driver loading or process tampering | More infrastructure, artifact provenance, privileges, or mechanisms; weak return for this bounded runtime comparison. Event 25 is not demonstrated by ordinary process launch. |
| Potential Direct Syscall of NtOpenProcess | Its CallTrace predicate starts with UNKNOWN. Inspect existing process-access captures as an exploratory diagnostic. Ordinary reference execution may not match; do not add handcrafted syscall mechanisms just to qualify the rule. |
| Vcruntime140 DLL sideloading | The rule explicitly filters a valid signed C Runtime Library. Ordinary CRT loading therefore does not automatically establish an alert difference. Do not replace the CRT with a fake unsigned DLL to manufacture the result. |
| More pipe/DNS/file-name/ADS-domain indicators | Often feasible but largely reuse current or proposed operations. Record incidental alerts as secondary observations; do not treat every string variant as an independent mechanism. |
| Named application or shell rules | Many require specific real process identities, metadata, or ancestry. Renaming a probe is not equivalent to reproducing the named application's behavior; wrappers would mainly measure the shared child tool. Retain genuinely needed identity fixtures only with an explicit rationale. |

The generic raw-read and non-.exe-execution Hayabusa rules are also recorded as reviewed alternatives. They are not Sigma-derived, unlike the current 52 primary targets, so adding them would require changing the stated corpus-origin scope. Generic raw-read can be recorded incidentally from the proposed Sigma raw-read experiment.

**Qualification and stopping rule**

1. Freeze a short behavior contract, exact target ID, inputs, independent receipt, shared fixtures, and no-behavior control before collecting outcomes. Rank cases by added mechanism or predicate dimension, not expected runtime differences.
2. Qualify the C reference first under the existing detector bytes/profile. Retain all failed behavior and collection attempts. If the behavior succeeds but the reference does not alert, keep the finding and defer that candidate from the qualified primary set.
3. Port identical logical behavior across the eight configurations. Hold compiler/OS/fixtures and runtime-independent helpers constant. Verify actual runtime linkage. Reject accidental baseline contamination; do not suppress or rename rules to clean controls.
4. Preserve valid alert misses in later configurations. Evaluate all enabled rules but distinguish predetermined primary targets from incidental matches. Keep the selection bias toward C-detectable behaviors explicit.
5. Retain native telemetry, raw EVTX, Hayabusa results, process identities, quality checks, and independent behavior receipts. Report actual valid denominators and invalid attempts.
6. Stop after the four-candidate qualification wave unless the optional remote-thread case adds a documented dimension worth its cost. Do not claim four additional qualified targets if fewer pass. Do not alter historical study counts or pool qualification runs into confirmatory data.

There is also an existing evidence-mapping task: rules for Active Setup and screensaver registry changes permit events 12/13/14, but their current programs perform writes rather than explicit registry renames. Similarly, several predicates permit multiple event IDs. Map observed target-event pathways before claiming event-family coverage. A deliberate rename variant might broaden behavior without increasing the unique-rule count; its exact target predicate needs separate review.

**Documentation correction**

The Windows coverage README says selected predicates reference 12 event IDs. The current 52-case selection JSON references **16**: 1, 2, 3, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 22, 23, 26. Twelve is the current number of cataloged behavior families. Neither number proves every permitted event pathway was exercised. This assessment records the discrepancy without editing the selection or changing the measured scope.

**Evidence files**

- [Summary](summary.json): verified source identity, corpus counts, existing family distribution, and review scope.
- [Candidate decisions](reviewed-candidates.csv): 29 reviewed rules, exact IDs, proposed cases, rationale, and source paths.
- [Predicate snapshots](reviewed-candidates.json): original detection clauses, hashes, authors, and pinned source links. Retained under the existing [Detection Rule License](../../ttp-composite/windows/coverage/RULE-LICENSE.md).
- [Original complete triage](../coverage-expansion/windows-rule-audit.csv): includes all 4,987 definitions; deferred rows remain deferred, not declared infeasible.
- [Current Sysmon profile](../../lab-environment/config/sysmon.xml) and [current attribution implementation](../../ttp-composite/windows/coverage/analyze.py).

The figures describe the pinned Hayabusa archive, not current upstream Sigma as a whole. The official Sysmon reference supports event semantics only; candidate predicates and counts come from the verified local archive.
