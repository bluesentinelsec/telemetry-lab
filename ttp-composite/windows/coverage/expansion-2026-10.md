# Windows behavior expansion, October 2026

Four standalone candidates extend the existing Windows suite. Their original
rule bytes and predicates are recorded in `selection.json`; the selection
rationale is in [the assessment](../../../docs/windows-rule-assessment/README.md).
Qualification results are recorded separately from historical measurements.

| Case | Operation and independent check | Sysmon target |
| --- | --- | --- |
| `unicode_child_arguments` | Spawn the fixed C reference helper with the single argument `marker\u00a0value` (U+00A0). The helper checks the exact UTF-16 command-line argument and returns 43 only for that value. | Event 1, Unicode command-line predicate |
| `ads_provenance_contents` | Write and read back the complete fixed ASCII Zone.Identifier payload on an owned `provenance.exe` carrier. The URL uses documentation address 192.0.2.1; there is no download, DNS lookup, or connection. | Event 15, Contents regex and stream filename |
| `raw_owned_volume_read` | Read exactly 512 bytes from the harness-owned virtual disk and check byte `i` equals `i % 251`. | Event 9, raw device read |
| `signed_system_library_load` | Require RstrtMgr.dll absent, load the genuine System32 library, verify the resulting module path, and unload it. No Restart Manager operation is invoked. | Event 7, module path/name |

The same-binary `--control` skips each operation. There is no multi-case
executable or per-runtime predicate adjustment. The Unicode helper bytes are
identical across configurations in the live lab; ordinary existing helper
invocations retain their marker and exit code 42.

C/C++ use CreateProcessW for Unicode spawning; Go and Rust use their standard
process APIs, which transport Unicode arguments on Windows. Stream writes use
C stdio, C++ fstreams, Go os file APIs, and Rust std::fs. Raw reads use Windows handle APIs
in each language. Library loading uses native Windows APIs or their bindings.
Native API use limits the possible runtime-mediated variation; equal outcomes
remain useful observations. C++ retains its standard-library output/linkage
markers and the existing PE import checks.

## Fixture ownership and evidence

The raw-read harness creates a fresh 16 MiB fixed VHD inside the new evidence
directory using diskpart. It writes the known sector pattern into that ordinary
file while detached, then mounts it read-only without a drive letter. It checks
that the resolved disk is neither a boot nor system disk and is read-only.
Only the device resolved from that specific image enters the probe environment.
No physical device is opened for writing. Teardown detaches the image, checks
that its complete SHA-256 is unchanged, and deletes the disposable image while
retaining creation, mapping, hash, and cleanup receipts. Setup is attributable
to the harness, not the measured probe.

The library fixture requires a valid Authenticode signature and records the
system library's path, SHA-256, and signer. The Windows image and library hash
must remain frozen throughout a campaign. Stream carriers are exclusively
owned and removed after every active/control attempt. Existing attribution
joins exact rule IDs and event record IDs to measured process GUIDs and their
descendants, allowing the Unicode child event to be scored without awarding
unrelated helper activity.

These are controlled observable conditions, not full attacks or proof of
end-to-end attacker success. Qualification must establish independent behavior,
healthy collection, reference target alerts, and clean controls before these
four increase the reported qualified scope.
