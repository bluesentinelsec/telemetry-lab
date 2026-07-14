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

## Scope and deferrals

This deliverable is the **instance happy path** only: both hosts deploy and run.
Deliberately **not** included yet (deferred until the happy path is settled):

- **Management channel (SSM Session Manager).** The hosts have no inbound access
  and no SSH key; the SSM access layer is the next increment.
- **Post-deploy configuration**: disabling Windows Defender, installing pinned
  toolchains and telemetry dependencies, and downloading pre-built primitives.

## Cost note

Two `c7i.xlarge` instances run roughly ~$0.20/hr (Debian) and ~$0.30/hr
(Windows, with license); gp3 storage is a few dollars/month per volume. The lab
is meant to be torn down when idle, so cost is per-use. A public-subnet VPC with
no NAT gateway adds nothing.
