# Composite rule coverage expansion

Tracked in [Linux #69](https://github.com/bluesentinelsec/telemetry-lab/issues/69)
and [Windows #70](https://github.com/bluesentinelsec/telemetry-lab/issues/70).
The implementation is stacked on PR #68 to retain its collection fixes and
explicit removal of the `.onion` test. Release publication is not part of this work.

## Selection and denominators

| Platform | Supplied rules | Enabled in measured profile | Existing targets | New targets | Planned total |
|---|---:|---:|---:|---:|---:|
| Falco Linux | 95 | 81 | 30 | 12 | 42 |
| Hayabusa Windows | 4,987 | 2,269 Sysmon | 23 | 30 | 53 |

These are distinct **primary target rules**, not every collateral match. They
are purposively selected behaviors and detection predicates, not a random
sample of all rules or an estimate of product-wide detection accuracy. Multiple
rules relying on file paths or DNS names do not represent independent OS
mechanisms. Report mechanism/family coverage alongside the rule counts.
Qualification status is separate from selection; new targets need real alert
and control evidence before being described as demonstrated.

The complete supplied corpora were inventoried. The Hayabusa release archive
SHA256 is `4d304cc5baaa750ed08cc24b7b89c58ea058740c7e344502d7b82554637543a8`;
all 4,987 inventory file hashes were checked against the downloaded archive.
`windows-rule-audit.csv` records automated whole-corpus eligibility/dependency
triage; `windows-plan.json` contains manually reviewed predicates and concrete
fixture inputs for this wave. Deferred-triage rows are **not claims of manual
feasibility review or impossibility**. Falco's 95-rule inventory records all
remaining exclusions, including its 14 stock-disabled rules. This expansion
does not change stock rule enablement or edit rule conditions.

Windows predicate snapshots retain upstream authors, pinned rule URLs, related IDs
and the [Detection Rule License 1.1](https://github.com/Yamato-Security/hayabusa-rules/blob/fffbdd179c8c8c7554368c443f9ba2917877f108/LICENSE.md).

Reproduce the audit with PyYAML installed and the pinned archive extracted:

```sh
python3 scripts/coverage-expansion/audit.py /path/to/hayabusa/rules
```

## Behavior contracts

Each case is a standalone program in C, C++, Go and Rust. The same case targets
the same exact rule in all eight configurations on its platform. Controls
start the same program and omit the tested operation. Language libraries are
used for ordinary file, process and networking operations. Missing standard
library capabilities use documented OS APIs; these cases provide less scope
for library-mediated differences and should be reported separately.

Linux adds native file access, namespace joining and an explicitly denied namespace-change request, `userfaultfd` and a minimal
unattached BPF socket-filter program. It also adds real launches of fixed grep,
base64 and dpkg utilities and a benign child environment-variable test. These
utility launches measure creation of the child; they do not reimplement grep
or package management in each language. The release-agent case exercises an
inert file matching the stock predicate with the required capability; it does
not alter a real cgroup or perform an escape. Host-path access reads only an
owned read-only fixture mount. Network namespaces and capabilities are local
to disposable containers; no host namespace is entered.

Windows adds ten registry changes, eight file creations, four fixture deletions,
four resolver queries, two named pipes, process access and remote thread
creation. Programs verify resulting bytes, values, return data or handles
independently of alerts. All registry values are saved/restored. Deletion tests
use only newly created owned fixtures, never genuine logs/history. A benign
real `ping.exe` is the process-access/thread target; the remote function simply
returns its process ID, and the child is terminated/reaped. No payload is
injected and no credential process is accessed.

The ErrorHandler.cmd candidate was replaced with `shim_database_file` after CI
found a pre-existing OS-owned ErrorHandler.cmd. The refusal to overwrite that
file remains intact. The inert .sdb file is never installed/registered.

DNS extends the existing approved local responder and temporary exact-name
NRPT approach. All selected names return 127.0.0.42 locally, requests are
logged server-side, cache/policy are cleaned up, and no external service is
contacted. `.onion` stays out of scope. These test DNS predicates, not the
application protocols or malware described in some rule titles.

Current live results and preserved prototype defects are recorded in
[the validation report](validation/README.md).

## Automated validation

Deploy using the existing CDK app, then stage CI artifacts and run campaigns:

```sh
cd lab-environment
npm ci
npx cdk deploy -c stackName=CoverageExpansion -c instanceType=m6i.large \
  -c diskGiB=100 --require-approval never --outputs-file /absolute/path/outputs.json
cd ..
python3 scripts/coverage-expansion/lab.py stage --os linux --phase stage \
  --stack CoverageExpansion --outputs /absolute/path/outputs.json \
  --evidence /absolute/path/evidence --ci-run BUILD_RUN_ID \
  --falco-archive /absolute/path/verified-falco-healthfix.tgz
python3 scripts/coverage-expansion/lab.py stage --os windows --phase stage \
  --stack CoverageExpansion --outputs /absolute/path/outputs.json \
  --evidence /absolute/path/evidence --ci-run BUILD_RUN_ID
python3 scripts/coverage-expansion/lab.py run --os linux --phase qualification \
  --stack CoverageExpansion --outputs /absolute/path/outputs.json \
  --evidence /absolute/path/evidence --repetitions 3
```

Repeat `run` for Windows. `--case` and `--config` can narrow development runs;
use `--repetitions 200` for the full experimental protocol. This invokes the
existing frozen-bundle experiment engine with default bounded retry, accepted
and suspect directories, exact attribution and complete raw captures. Valid
misses are retained, not retried to earn an alert. Both this launcher and the underlying experiment CLI provide `--no-retry` and
`--max-retries`. The launcher allows up to 48 hours per SSM command; use
`--execution-timeout` to shorten it or split larger 200-repetition campaigns
by `--case`/`--config` when a single host would exceed that limit.

`status` reads a preserved SSM command receipt. `collect` downloads results and
SSM evidence. Each phase name must be new; no previous evidence is overwritten.
Archive and verify local results before destroying the task's CDK stack.
The Falco archive is the existing narrow 0.45.0 collector-health fix; staging
records its archive hash and verifies its binary against its build receipt.
Hayabusa and the complete rule corpus are verified before every Windows capture.
