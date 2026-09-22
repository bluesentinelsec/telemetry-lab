# Refined Windows network TTP Composite scope

Status: seven proposed standalone cases targeting seven unmodified rules; not yet lab-qualified. These replace the earlier network/DNS candidate subset. The overall proposal remains 24 candidates. Subject: the inventoried Hayabusa 4.1.0 Windows release bundle, with exact rule IDs and hashes in `selection.json`.

## Decision

Use only two measured operation families: TCP connect/send/receive/close and ordinary hostname-to-address resolution. This follows the existing `tcp_client` and `dns_lookup` primitives. The original working checkout already contains a Winsock implementation of the C TCP primitive; the scope worktree predates those uncommitted changes, which must be preserved when implementation begins.

Keep four destination-port rules. Their titles mention SMTP, RDP, ADWS, and Kerberos, but their predicates evaluate Sysmon EID 3 connection metadata: initiated connection, destination port, and process exclusions. None requires an application handshake, successful authentication, protocol parsing, TLS, or a third-party protocol library. A fixed TCP byte exchange is sufficient to attempt those predicates and independently prove completed I/O. These are port-based detection tests, not protocol simulations.

Replace the LDAP-discovery DNS candidate with a TCP connection from a rule-listed executable location. The LDAP rule actually checks a `_ldap.` QueryName prefix, not LDAP traffic or an SRV query type; the earlier SRV requirement was unnecessarily specific. Defer it to keep the first pass focused on the two existing lookup targets.

## Exact target mapping

| Case | Measured behavior | Exact bundled rule | Rule ID |
|---|---|---|---|
| `tcp_connect_2525` | TCP exchange to private peer:2525 | Suspicious Outbound SMTP Connections | `f8a59cdc-b3d1-8f59-c3f4-4db6d94e8efc` |
| `tcp_connect_3389` | TCP exchange to private peer:3389 | Outbound RDP Connections Over Non-Standard Tools | `f3fa6209-076f-c860-c7cb-e2f6bdd7d3e0` |
| `tcp_connect_9389` | TCP exchange to private peer:9389 | Uncommon Connection to Active Directory Web Services | `ae8c1c58-4743-c0c8-3b30-7d69f7cbee68` |
| `tcp_connect_88` | TCP exchange to private peer:88 | Uncommon Outbound Kerberos Connection | `322fd5f2-b5b7-1bf4-58f2-92873dc878bb` |
| `tcp_connect_public_path` | TCP exchange to private peer:49152 from C:\Users\Public\telemetry-lab\probe.exe | Network Connection Initiated From Process Located In Potentially Suspicious Or Uncommon Location | `df13f270-859b-272a-9c2a-a0ef744a0480` |
| `dns_onion` | Resolve lab.onion through isolated lab DNS | DNS Query Tor .Onion Address - Sysmon | `29e2035f-b91f-3c35-9a7a-087b864f6d3b` |
| `dns_ip_lookup` | Resolve api.ipify.org through isolated lab DNS | Suspicious DNS Query for IP Lookup Service APIs | `e1d5e512-66be-e3eb-e24b-a9f3545e115a` |

The four port cases share the same socket behavior and differ only in the fixed destination port. This increases rule coverage, not the number of independent networking mechanisms. The executable-location case adds a different rule predicate. The two DNS cases use different name predicates with the same resolver operation.

## Fixtures and qualification

- **TCP:** use a harness-owned private peer with listeners on the five fixed ports. The peer echoes a fixed marker; both sides verify complete send/receive, handling partial I/O and bounded timeouts. No SMTP/RDP/ADWS/Kerberos server is needed. Keep the peer and its logging outside the measured process, and capture its receipt independently.
- **Network placement:** use a separate reachable peer rather than depending on loopback telemetry. The selected five rules have no blanket private-address exclusion. Actual Sysmon capture still needs a C qualification run. Hold address family, peer address, port, payload, attempt count, and executable path constant for each case across languages. Do not rename a binary to a trusted application to exploit or bypass a rule's exclusions.
- **Executable location:** stage the location-sensitive binary before the capture window. Its own initiated connection must generate the target event; merely creating a file in Public is insufficient. Use a controlled peer name such as `peer.lab.test`, outside the rule's excluded hostname suffixes. A raw-IP destination's actual DestinationHostname must be checked during qualification, not assumed.
- **DNS:** call the normal language resolver against an isolated system DNS configuration. The resolver supplies deterministic local answers for `lab.onion` and `api.ipify.org`; it must not forward them publicly. Resolve only—do not connect to either named service. Use no HTTP client, Tor client, LDAP library, custom DNS protocol implementation, or hosts-file substitution. Confirm the lookup result and resolver-side query evidence separately from Sysmon.
- **DNS cache:** establish and record the same cache baseline before every active/control attempt. Record query names, address family behavior, results and resolver traffic. A cached lookup or missing sensor event must not be mistaken for failed behavior. Qualification must show that the C baseline emits an attributable EID 22; rejection of a special-use name is a fixture/behavior issue to resolve, not automatically a detection miss.
- **APIs:** C/C++ use Windows socket/resolver APIs, Go uses its standard `net` library, and Rust uses its standard networking facilities. Preserve the existing compiler/runtime axes and verify their actual Windows resolver behavior; do not assume Go's cgo/pure-Go Windows builds select different resolvers or force every language through a shared external implementation.
- **Controls:** run each same binary at the same path with the target operation disabled. Retain neutral behavior controls during initial qualification: the same TCP exchange on a non-target port, the location-sensitive exchange from a neutral path, and a neutral DNS name. These show that a matching connection/query predicate matters; they do not replace the same-binary no-behavior control.
- **Attribution:** score exact bundled rule IDs and correlate their event records with the measured process identity and capture window. Require independent behavior success and a C baseline alert, then preserve valid misses in later runtime configurations. No alert alone is insufficient evidence of a runtime effect.

## Outside the initial network scope

- Protocol clients, authentication exchanges, real mail/remote-desktop/domain services, HTTP/TLS, external cloud metadata, or public C2 endpoints.
- Callback-port and uncommon-port rules that exclude loopback/private destinations; keep these deferred until there is a justified, isolated fixture satisfying their unchanged predicates.
- Rules tied to specific system applications, browser processes, or named offensive tools, where wrappers or masquerading would dominate the test.
- Inbound-server and standalone UDP cases: retain those as primitive-level operations unless a suitable unmodified rule and attributable positive control are separately selected. Do not promise arbitrary accept/read/write/socket-close rule coverage from this EID 3/EID 22 subset.

## Counts and next implementation step

Seven network-related candidate rules: five EID 3 targets and two EID 22 targets. They remain part of the 24-rule overall proposed Windows scope; 17 other candidates are unchanged. The 2,455 Sysmon-referencing definitions and 2,269 statically eligible definitions in the pinned inventory remain unchanged. These are corpus counts, not counts of network rules, loaded rules, or confirmed alerts.

Implement and qualify C first, then port identical behaviors and exact target IDs to C++, Go, and Rust. No lab has been deployed for this scope refinement. Track implementation in issue #59.
