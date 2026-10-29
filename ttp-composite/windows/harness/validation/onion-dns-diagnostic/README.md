# Local DNS record diagnostic

The user requested testing a hard-coded local DNS record for `lab.onion` before changing the composite contract. The server returned `lab.onion A 127.0.0.42` to a direct UDP query, but the unchanged C programs could not obtain that answer through the Windows resolver on this Windows Server 2025 image. This approach is **not adopted** for the `.onion` composite; 23 targets remain qualified in both CRTs.

| Configuration | UCRT `lab.onion` | MSVCRT `lab.onion` | `api.ipify.org` control lookup |
|---|---|---|---|
| Exact-name NRPT policy, immediate | WSAHOST_NOT_FOUND (11001) | WSAHOST_NOT_FOUND (11001) | Success in both CRTs |
| Same policy after 10 seconds; cache cleared | WSAHOST_NOT_FOUND (11001) | WSAHOST_NOT_FOUND (11001) | Success in both CRTs |
| Adapter DNS server temporarily set to 127.0.0.1 | WSAHOST_NOT_FOUND (11001) | WSAHOST_NOT_FOUND (11001) | Success in both CRTs |

The direct wire query verifies the server record independently of Windows' resolver. The server log contains its one diagnostic query for `lab.onion`; the subsequent C lookups do not reach the responder. `Resolve-DnsName -Server 127.0.0.1 -DnsOnly -NoHostsFile` also rejects `lab.onion`, while it resolves `api.ipify.org`. The result is consistent across both CRTs and is not a runtime-induced difference.

These 12 program invocations are **diagnostics, not additional qualification attempts**: they do not include same-binary no-operation controls or replace the existing 100-attempt follow-up summary. No measured program, expected-success condition, detection rule, or hosts-file entry was changed. The server and program binaries are from CI workflow 35729429141, commit `a712ce9`, also used for the preceding qualification.

Temporary NRPT entries were removed; the adapter's original DHCP DNS mode and server 10.0.0.2 were restored and verified before teardown. `onion-dns-provenance/restore-verification.json` records the checks. Raw EVTX and complete diagnostic evidence are in the hash-verified local `windows-c-onion-dns.tgz` archive identified by `archive-manifest.json`. The stored scripts reproduce the exact diagnostic steps; their S3 locations and instance details describe this disposable run.
