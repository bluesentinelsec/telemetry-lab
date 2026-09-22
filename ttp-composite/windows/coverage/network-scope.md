# Refined Windows network TTP Composite scope

Status: seven standalone cases targeting seven unmodified rules; approved local fixtures are undergoing qualification. These replace the earlier network/DNS candidate subset. The overall proposal remains 24 candidates. Subject: the inventoried Hayabusa 4.1.0 Windows release bundle, with exact rule IDs and hashes in `selection.json`.

## Decision

Use only two measured operation families: TCP connect/send/receive/close and ordinary hostname-to-address resolution. This follows the existing `tcp_client` and `dns_lookup` primitives. The original working checkout already contains a Winsock implementation of the C TCP primitive; the scope worktree predates those uncommitted changes, which must be preserved when implementation begins.

Keep four destination-port rules. Their titles mention SMTP, RDP, ADWS, and Kerberos, but their predicates evaluate Sysmon EID 3 connection metadata: initiated connection, destination port, and process exclusions. None requires an application handshake, successful authentication, protocol parsing, TLS, or a third-party protocol library. A fixed TCP byte exchange is sufficient to attempt those predicates and independently prove completed I/O. These are port-based detection tests, not protocol simulations.

Replace the LDAP-discovery DNS candidate with a TCP connection from a rule-listed executable location. The LDAP rule actually checks a `_ldap.` QueryName prefix, not LDAP traffic or an SRV query type; the earlier SRV requirement was unnecessarily specific. Defer it to keep the first pass focused on the two existing lookup targets.

## Exact target mapping

| Case | Measured behavior | Exact bundled rule | Rule ID |
|---|---|---|---|
| `tcp_connect_2525` | TCP exchange to 127.0.0.1:2525 | Suspicious Outbound SMTP Connections | `f8a59cdc-b3d1-8f59-c3f4-4db6d94e8efc` |
| `tcp_connect_3389` | TCP connect/send to existing RDP at 127.0.0.1:3389 | Outbound RDP Connections Over Non-Standard Tools | `f3fa6209-076f-c860-c7cb-e2f6bdd7d3e0` |
| `tcp_connect_9389` | TCP exchange to 127.0.0.1:9389 | Uncommon Connection to Active Directory Web Services | `ae8c1c58-4743-c0c8-3b30-7d69f7cbee68` |
| `tcp_connect_88` | TCP exchange to 127.0.0.1:88 | Uncommon Outbound Kerberos Connection | `322fd5f2-b5b7-1bf4-58f2-92873dc878bb` |
| `tcp_connect_public_path` | TCP exchange to 127.0.0.1:49152 from C:\Users\Public\telemetry-lab\probe.exe | Network Connection Initiated From Process Located In Potentially Suspicious Or Uncommon Location | `df13f270-859b-272a-9c2a-a0ef744a0480` |
| `dns_onion` | Resolve lab.onion through isolated lab DNS | DNS Query Tor .Onion Address - Sysmon | `29e2035f-b91f-3c35-9a7a-087b864f6d3b` |
| `dns_ip_lookup` | Resolve api.ipify.org through isolated lab DNS | Suspicious DNS Query for IP Lookup Service APIs | `e1d5e512-66be-e3eb-e24b-a9f3545e115a` |

Three port cases and the path case use a fixed echo exchange; RDP uses connect/send against the existing listener without authentication. This increases rule coverage, not the number of independent networking mechanisms. The executable-location case adds a different rule predicate. The two DNS cases use different name predicates with the same resolver operation.

## Fixtures and qualification

- **TCP:** harness-owned echo listeners on 127.0.0.1 ports 88, 2525, 9389 and 49152 verify the fixed marker exchange. Port 3389 uses the existing RDP listener and an 11-byte X.224 request; successful connect and complete send are checked without requiring an echo or establishing an authenticated session. No service is stopped or reconfigured.
- **Network placement:** qualification confirmed Sysmon captures loopback connections. Hold IPv4 address, port, payload, attempt count and executable path constant across languages. All five TCP programs and their controls wait five seconds after I/O (or skipped I/O). This fixed lifetime is part of the experimental contract; earlier immediate-exit observations remain in the evidence.
- **DNS:** call the normal language resolver against temporary exact-name NRPT policies directing only the two names to a harness-only UDP responder at 127.0.0.1:53. The responder supplies 127.0.0.42 with zero TTL as deterministic local answers for `lab.onion` and `api.ipify.org`; it must not forward them publicly. Resolve only—do not connect to either named service. Use no HTTP client, Tor client, LDAP library, custom DNS protocol implementation, or hosts-file substitution. Confirm the lookup result and resolver-side query evidence separately from Sysmon.
- **DNS cache:** establish and record the same cache baseline before every active/control attempt. Record query names, address family behavior, results and resolver traffic. A cached lookup or missing sensor event must not be mistaken for failed behavior. Qualification must show that the C baseline emits an attributable EID 22; rejection of a special-use name is a fixture/behavior issue to resolve, not automatically a detection miss.
- **APIs:** C/C++ use Windows socket/resolver APIs, Go uses its standard `net` library, and Rust uses its standard networking facilities. Preserve the existing compiler/runtime axes and verify their actual Windows resolver behavior; do not assume Go's cgo/pure-Go Windows builds select different resolvers or force every language through a shared external implementation.
- **Controls:** run each same binary at the same path with the target operation disabled. Additional neutral-port/path/name experiments can support predicate analysis; these are not counted as completed qualification controls.
- **Attribution:** score exact bundled rule IDs and correlate their event records with the measured process identity and capture window. Require independent behavior success and a C baseline alert, then preserve valid misses in later runtime configurations. No alert alone is insufficient evidence of a runtime effect.

## Outside the initial network scope

- Protocol clients, authentication exchanges, real mail/remote-desktop/domain services, HTTP/TLS, external cloud metadata, or public C2 endpoints.
- Callback-port and uncommon-port rules that exclude loopback/private destinations; keep these deferred until there is a justified, isolated fixture satisfying their unchanged predicates.
- Rules tied to specific system applications, browser processes, or named offensive tools, where wrappers or masquerading would dominate the test.
- Inbound-server and standalone UDP cases: retain those as primitive-level operations unless a suitable unmodified rule and attributable positive control are separately selected. Do not promise arbitrary accept/read/write/socket-close rule coverage from this EID 3/EID 22 subset.

## Counts and next implementation step

Seven network-related candidate rules: five EID 3 targets and two EID 22 targets. They remain part of the 24-rule overall proposed Windows scope; 17 other candidates are unchanged. The 2,455 Sysmon-referencing definitions and 2,269 statically eligible definitions in the pinned inventory remain unchanged. These are corpus counts, not counts of network rules, loaded rules, or confirmed alerts.

Implement and qualify C first, then port identical behaviors and exact target IDs to C++, Go, and Rust. No lab has been deployed for this scope refinement. Track implementation in issue #59.
