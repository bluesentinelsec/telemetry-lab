# lab-environment

An AWS CDK app that deploys the disposable lab for the telemetry-lab study: one
**Debian 13** host and one **Windows Server 2025** host, both `x86_64`, in a
dedicated minimal VPC. It is designed to be deployed and torn down frequently,
and to run under **any** AWS account with no code changes.

## What it deploys

| Host | AMI source | Instance | Root disk |
|---|---|---|---|
| Debian 13 (trixie) | Debian owner AMI, resolved by name/owner filter | `c7i.xlarge` | 150 GiB gp3 |
| Windows Server 2025 | `Windows_Server-2025-English-Full-Base` SSM parameter | `c7i.xlarge` | 150 GiB gp3 |

Plus a dedicated VPC (public subnets, internet gateway, **no NAT gateway**) and
one egress-only security group per host (all outbound, **zero inbound**).

Both hosts come up **detection-ready** via user data, with the solutions under
test installed at their **latest** release (not pinned — see *Provenance* below):

| Host | Detection stack | Role |
|---|---|---|
| Debian 13 | **Falco** (modern-eBPF driver, default + incubating + sandbox rules) | syscall-level detector |
| Windows Server 2025 | **Sysmon** (log-all config) + **Hayabusa** (bundled Sigma ruleset) | event-level detector |

Both hosts also fetch the latest **telemetry-lab release bundle** (`tmon`, `tap`,
`ttp-primitives`, substrate manifests) at boot and extract it under `/opt/lab`
(Linux) / `C:\lab\telemetry-lab` (Windows), so a fresh host is experiment-ready.

These OS/instance choices mirror the CI runners so the runtime substrate matches:
Debian 13 is the `debian:trixie` container CI builds in, and Windows Server 2025
is the `windows-2025` runner.

## Prerequisites

- Node.js 18+ and npm
- AWS credentials for the target account (`aws sts get-caller-identity` should succeed)
- The account/region **bootstrapped** once for CDK (below)

## Deploy

```sh
cd lab-environment
npm install

# One-time per account+region:
npx cdk bootstrap

# Preview the CloudFormation, then deploy:
npx cdk synth
npx cdk deploy

# Tear it all down (VPC, instances, everything):
npx cdk destroy
```

## Portability

The app hardcodes nothing account- or region-specific, so a different
practitioner just points their credentials at their own account and deploys:

- **Account** comes from the deploying credentials (`CDK_DEFAULT_ACCOUNT`).
- **AMIs** are resolved dynamically (Debian by owner+name filter; Windows by SSM
  parameter), never by a hardcoded AMI ID, so they are correct in any region.
- **No key pairs, no pre-created S3 buckets, no hardcoded resource names** — so
  there is nothing to set up by hand and nothing that can collide with another
  account (e.g. globally unique S3 bucket names).
- `cdk.context.json` is git-ignored so the Debian AMI lookup re-resolves per
  account instead of pinning to whoever synthesized first.

## Configuration

Defaults are set for this study; override any of them at deploy time without
editing code:

| Setting | Default | Override |
|---|---|---|
| Region | `us-west-2` | `-c region=us-east-1` |
| Instance type | `c7i.xlarge` | `-c instanceType=c7i.2xlarge` |
| Root disk (GiB) | `150` | `-c diskGiB=100` |

```sh
npx cdk deploy -c region=us-east-1 -c instanceType=c7i.2xlarge -c diskGiB=100
```

## Access (SSM)

Both hosts are managed via AWS Systems Manager — no inbound ports, no SSH keys.
Each carries the `AmazonSSMManagedInstanceCore` permissions; Windows Server ships
the SSM agent, and Debian installs it at boot. Once the instances register
(`aws ssm describe-instance-information`), run commands with `aws ssm
send-command` or open a shell with `aws ssm start-session --target <id>`.

## Provenance (inventory)

Each host self-inventories as the **last provisioning step**, writing a
deterministic `inventory.json` — version + SHA-256 + path for every significant
component (the telemetry-lab release and its `tmon`/`tap`/`ttp_primitives`, the
detectors, and the OS):

| Host | Inventory file | Written by |
|---|---|---|
| Debian 13 | `/opt/lab/inventory.json` | `scripts/inventory-linux.sh` |
| Windows Server 2025 | `C:\lab\inventory.json` | `scripts/inventory-windows.ps1` |

Both scripts are embedded into user data at synth (the files under `scripts/` are
the source of truth). Because the lab consumes **latest** dependencies (so it
never breaks on an upstream change), this per-host inventory — not a version pin —
is what establishes reproducibility: an experiment completes within a day, and the
file records exactly what ran.

**`tap` consumes it.** When `tap` finds an `inventory.json` co-located with the
telemetry it analyzes, it embeds it under `provenance` in `analysis.json` and
renders it as a Provenance section in `report.md` — so every result traces back to
the exact versions + hashes that produced it. Collect `inventory.json` alongside
raw telemetry so it travels with the data.

## Validate the deploy

`scripts/validate-linux.sh` / `validate-windows.ps1` prove the detection pipeline
actually fires, end to end (Falco canary + `/etc/shadow` rule on Linux;
Sysmon → EVTX → Hayabusa/Sigma on Windows). Run them over SSM after a deploy:

```sh
# Linux (Falco): canary rule + read /etc/shadow -> expect an alert
aws ssm send-command --instance-ids <debian-id> \
  --document-name AWS-RunShellScript \
  --parameters commands="bash /path/validate-linux.sh"

# Windows (Sysmon + Hayabusa): recon + Run-key write -> expect >=1 Sigma detection
aws ssm send-command --instance-ids <windows-id> \
  --document-name AWS-RunPowerShellScript \
  --parameters commands="powershell -File C:\\lab\\validate-windows.ps1"
```

## Scope and deferrals

Still deferred (not part of this app yet):

- **Per-experiment overrides**: swapping in a specific pinned telemetry-lab build
  (rather than latest) for a given experiment run is done by re-staging the
  bundle, not by this app.

## Cost note

Two `c7i.xlarge` instances run roughly ~$0.20/hr (Debian) and ~$0.30/hr
(Windows, with license); gp3 storage is a few dollars/month per volume. The lab
is meant to be torn down when idle, so cost is per-use. A public-subnet VPC with
no NAT gateway adds nothing.
