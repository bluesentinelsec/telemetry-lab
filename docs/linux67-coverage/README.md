# Linux Falco supplied-rule coverage expansion

Status: implemented and live-qualified on 2026-09-30. Tracks #73 and PR #74.

The qualified selection is **67 of 95 supplied rules (70.5%)**: 42 existing targets plus 25 additions. The upstream corpus remains byte-identical. A separate profile enables seven previously disabled rules, bringing the enabled evaluation profile from 81 to 88 rules. Thus the same numerator is 67/88 (76.1%) of this expanded profile. Neither denominator is a random-sampling frame for estimating product-wide effectiveness.

The suite has one standalone program per case in C, C++, Go and Rust, across eight configurations. Utility versions, service fixtures, operation inputs and rule predicates are fixed across the configurations. Library-mediated operations, fixed-utility launches and application-ancestry cases are distinguished in the catalog. Multiple rules may describe one mechanism or overlapping behavior; 67 target rules do not imply 67 independent mechanisms or complete adversary intrusions.

## Automation and constraints

The existing CDK app provisions a disposable Linux host; `scripts/coverage-expansion/lab.py` stages CI artifacts, builds the shared image, starts the pinned detector, and runs the retry-enabled experiment engine. The image installs utilities and a SHA-256-pinned Bun 1.3.0 binary. Services, accounts, keys, filesystem images, FIFO gates, and private endpoints are created automatically before the measurement window. Containers have no external network route. Privileged cases touch only their owned mount/image fixtures. No host namespace or host filesystem device is targeted.

The miner-pool rule requires a listed domain as well as a port. Its supplied domain lists resolve to the private fixture address through an automated detector-host hosts-file block; no miner service is contacted and no predicate is rewritten. Dependency inventories, image IDs and the name-resolution receipt are archived.

The web-server ancestry cases use actual Apache CGI execution, without renaming the native program or spoofing an application process name. The package-install case starts its installer before capture, waits at a FIFO gate, and launches the native executable only after capture starts. The fixed child tool performs a verified marker exchange. Same-binary controls preserve the surrounding fixture and omit the measured operation.

## Development findings retained

- The initial C reference campaign demonstrated 23 of 25 added targets, with all 25 controls clean. The Docker daemon package did not include `/usr/bin/docker`; setup now explicitly installs `docker-cli`.
- Real `npm install` changed its process name to `npm install`, which fails the unchanged rule's exact package-manager-name predicate. That successful behavior/no-alert observation is retained. The qualified fixture uses real Bun, explicitly listed by the stock rule, to execute the same local npm-package lifecycle. No native executable or rule was changed to disguise the package manager.
- Both corrected reference cases subsequently demonstrated their target alerts and clean controls. Original failures and the initial npm valid miss remain separate from the final qualification.
- Full-matrix testing exposed an interactive-shell fixture race: echoed input could be mistaken for executed output, followed by premature socket closure. The diagnostic also reproduced a missing-receipt failure when the child completed before the server wrote its verification file. The corrected exchange has a marker absent from its command text and an acknowledgment after receipt publication and before shell exit. All eight configurations are requalified for that case; every original observation is retained and superseded, including those that passed.

`k8s_client` uses the real stock-listed Docker CLI's `--version` operation, requiring no daemon or Kubernetes cluster. This measures the tool-launch predicate. `identity_change` performs and verifies a successful drop from root to the named fixture UID 2000. Port and file-indicator cases reproduce the rule predicates, not the broader attack implied by every rule title.

## Additional target catalog

| Case | Exact target rule | Upstream enablement |
| --- | --- | --- |
| `identity_change` | Non sudo setuid | enabled |
| `interactive_recon` | Basic Interactive Reconnaissance | enabled |
| `netcat_exec` | Netcat Remote Code Execution in Container | enabled |
| `bulk_clear` | Remove Bulk Data from Disk | enabled |
| `ssh_nonstandard` | Disallowed SSH Connection Non Standard Port | enabled |
| `shell_network` | System procs network activity | enabled |
| `proxy_environment` | Program run with disallowed http proxy env | enabled |
| `network_tool` | Launch Suspicious Network Tool in Container | enabled |
| `remote_copy` | Launch Remote File Copy Tools in Container | enabled |
| `ingress_copy` | Launch Ingress Remote File Copy Tools in Container | enabled |
| `privileged_mount` | Mount Launched in Privileged Container | enabled |
| `privileged_debugfs` | Debugfs Launched in Privileged Container | enabled |
| `k8s_client` | Kubernetes Client Tool Launched in Container | enabled |
| `protected_shell` | Run shell untrusted | enabled |
| `web_shell` | Web Server Spawned Shell | enabled |
| `web_child` | Web Server Spawned Suspicious Child Process | enabled |
| `web_reverse_shell` | Reverse Shell from Web Server | enabled |
| `npm_network_tool` | Network Tool Executed During NPM Package Install | enabled |
| `shell_config_read` | Read Shell Configuration File | enabled by explicit evaluation profile |
| `hidden_file` | Create Hidden Files or Directories | enabled by explicit evaluation profile |
| `executable_chmod` | Container Drift Detected (chmod) | enabled by explicit evaluation profile |
| `executable_create` | Container Drift Detected (open+create) | enabled by explicit evaluation profile |
| `nodeport_exchange` | Unexpected K8s NodePort Connection | enabled by explicit evaluation profile |
| `miner_port_exchange` | Detect outbound connections to common miner pool ports | enabled by explicit evaluation profile |
| `unexpected_inbound` | Unexpected inbound connection source | enabled by explicit evaluation profile |

## Reproduce the qualification

From a CDK-deployed Linux-only stack, stage the eight Linux composite CI artifacts
with `scripts/coverage-expansion/lab.py stage` and the pinned Falco health-fix archive.
With `STACK`, `OUTPUTS` and `EVIDENCE` set to the deployed stack name, CDK outputs
file and evidence directory, use:

```sh
python3 scripts/coverage-expansion/lab.py run --os linux --phase full-matrix-01 --repetitions 1 --stack "$STACK" --outputs "$OUTPUTS" --evidence "$EVIDENCE"
python3 scripts/coverage-expansion/lab.py collect --os linux --stack "$STACK" --outputs "$OUTPUTS" --evidence "$EVIDENCE"
```

The retained development campaign also has a three-repetition `web-recheck-01`
phase after the shell fixture correction. It supersedes that case's entire initial
active/control set. `scripts/coverage-expansion/audit-linux67.py RAW_LINUX OUTPUT`
checks the retained campaign's exact roster, valid behavior and collection,
clean controls/baselines, reference target coverage, preserved valid misses,
and target-alert counts. A fresh run from the final branch uses the corrected
fixture from the outset and does not need this historical supersession step.

## Qualification results

The CDK-deployed Debian host completed the full 67-case × eight-configuration
matrix: 1,080 scheduled observations (active, control and startup baselines).
Eight behavior failures in the web reverse-shell fixture were logged under
`suspect/` and automatically replaced, giving 1,088 attempts and 1,080 valid
observations. All other cases completed without retries. After correcting that
fixture, all 48 additional web reverse-shell observations (three active/control
repetitions × eight configurations) passed on their first attempt.

The final view supersedes all 16 original web reverse-shell observations with
those 48 corrected observations: **1,112 valid observations, 536 case/configuration
pairs, 552 clean same-binary controls and eight clean startup baselines**.
All 67 exact target rules fired in the C/glibc reference. Every one of the 25
added targets fired in every configuration; the original Go reverse-shell miss
remains in both Go configurations. Thus 534 of 536 pairs have positive-alert and
clean-control evidence, while all 536 have valid behavior and control evidence.
No collector-health failures or contaminated controls were accepted.

New alert-count differences were observed:

- `identity_change`: C, C++ and Rust produced one target alert; Go/cgo produced
  five and Go/static four. The alert records identify repeated `setuid` events.
- `miner_port_exchange`: Rust/GNU and Rust/musl produced three target alerts
  (one `connect`, two `sendto`); all other configurations produced one `connect`
  alert for the equivalent verified marker exchange.
- The existing `reverse_shell` case produced zero target alerts in both Go
  configurations and three in each C/C++/Rust configuration.

These are observed qualification results, not estimates of stable alert rates.
Most cases have only one active observation per configuration; repeated collection
is needed to distinguish repeatable runtime effects from run-to-run variation.
The initial npm-identity miss and invalid shell-fixture attempts are development
findings, not runtime findings. This is composite qualification, not the formal
200-repetition experiment or a new primitive-telemetry collection campaign.

Machine-readable results: [per-case/configuration qualification](validation/qualification.csv)
and [campaign summary](validation/summary.json). Raw journals, alerts, output,
health metrics, retry chains, immutable native artifact archive, image/package
inventories and SSM receipts are retained under
`/Users/michaellong/telemetry-lab-data/linux67-2026-09-30/`.
Native artifacts came from CI run `36756011609` at `61c05fd`; native source and
ELF hashes remained unchanged through both fixture refreshes. `fixture-03`
qualified the full matrix and `fixture-04` qualified the corrected shell case.

## Archive and teardown

All 8,909 raw evidence objects (210,346,468 bytes) were verified against S3
before deletion; the local SHA-256 inventory is retained under `checksums/`.
CDK destroyed `Linux67Coverage20260930`; the instance is terminated and the
stack and bucket are absent. See [archive receipt](validation/archive-receipt.json)
and [teardown receipt](validation/teardown-receipt.json).
