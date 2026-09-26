# Experiment collection and replacement contract

Run on one disposable lab host at a time with Python 3.11+ and the usual root /
Administrator collector permissions. Linux composites also require PyYAML
(`python3-yaml` on Debian), as does the existing qualification runner. The runner is included as `experiment/` in
new release bundles; it also runs directly from this repository. The existing
qualification/smoke-test runners remain available for diagnosis and do not fill
experiment quotas automatically.

```sh
python3 experiment/run.py /path/to/bundle /path/to/new-evidence \
  --cohort primitives --repetitions 200 --inventory /path/to/inventory.json
python3 experiment/run.py /path/to/bundle /path/to/new-composite-evidence \
  --cohort composites --repetitions 200 --image lab-falco-coverage:local
```

Windows uses the same Python CLI (`python` instead of `python3`). Composite
collection requires the pinned Sysmon/Hayabusa installation, fixed helper.exe and
fixture.node staged in `C:\lab\windows-coverage\fixtures`, and the existing RDP
listener. TCP/DNS fixtures use the existing local-only fixture scripts, including
exact-name temporary DNS policies. No third-party network services are added.
The Windows composite scope contains 23 cases per configuration, including the
working `dns_ip_lookup` case. The unsuccessful `.onion` case has been removed.

`--case NAME` and `--config NAME` can be repeated to select a subset. Repetitions
are per test/configuration and per active/control mode. Linux also includes one
negative-control program per configuration. With multiple hosts, divide the
intended count across hosts explicitly: `--repetitions 200` means 200 **on this
host**, not 200 across a fleet. Blocks are shuffled using the recorded `--seed`.

## Acceptance and retry

- Default: three replacement attempts after the initial attempt. Configure with
  `--max-retries N`; `--no-retry` (or `--max-retries 0`) disables replacement.
- Collector failure, loss, malformed/truncated telemetry, failed attribution, or
  an identified infrastructure failure is eligible. Recovery and health checks
  precede the replacement. Falco uses the same binary, image, configuration and
  rules; tmon creates a fresh collector session. Sysmon restarts only if stopped.
- A valid missing alert is **accepted**. A valid alert on a control is also
  accepted and reported. Neither is retried to manufacture the expected outcome.
- Native nonzero exit, failed behavior marker, or ambiguous native timeout is
  preserved as a behavioral failure without automatic replacement. Investigate
  before attributing such failures to infrastructure.
- Changed artifacts, unknown errors, and unsafe fixture state abort the campaign.
  Retry exhaustion leaves a slot unresolved and exits nonzero. The summary cannot
  claim completion unless every planned slot has an accepted measurement.

Every native composite execution uses a separate case program. Active and control
slots are separate: retrying a failed active measurement never repeats a valid
control. Composite collection defaults to one independently checked capture per execution.
`--batch-size 16` (Linux) or `--batch-size 48` (Windows) optionally shares a
capture/drain/evaluation across serial native executions. Linux keeps a fresh
container per execution and excludes setup by event timestamp; Windows freezes one
runtime's DLLs per group and attributes each attempt by its process GUID. Programs
never run concurrently on one host. Shared capture failure invalidates all affected
measurements. Only invalid slots are replaced, individually, with the ordinary
collector; accepted peers and valid misses are never repeated. Native behavior
failures remain terminal. Batch size and exact execution order are recorded in the
plan. Measure actual throughput; the pilot's timing is not a promise.

## Evidence layout

```
plan.json                  stable planned run IDs and retry policy
provenance.json            frozen inputs and environment
attempts.jsonl             every finalized attempt, including replacements
accepted.jsonl             only accepted attempts; one per resolved slot
summary.json               completion, retries, unresolved slots, per-cell counts
accepted/<attempt-id>/     accepted raw telemetry, logs, health and result
suspect/<attempt-id>/      rejected attempts with the same evidence retained
in-progress/<attempt-id>/  interrupted/unfinalized evidence requiring review
batches/<batch-id>/        shared original captures, health, fixture/cleanup logs
```

Each attempt records its logical run ID, unique attempt ID, replaced attempt ID,
repetition, timestamps and rejection reason. Writes are flushed before evidence
is moved out of `in-progress`. Never reuse an output directory. A hard interruption
may leave an unfinished directory: it is not accepted and must be audited before
starting a new campaign. No automatic resume silently guesses whether it ran.

For primitive analysis, point `tap` at `accepted/`, **not the campaign root**.
Keep suspect data and the full ledger for operational failure reporting. Accepted
measurements are conditional on collection validity; failures/retries must also be
reported by runtime. Do not pool pilot observations into confirmatory collection.

A shared capture can contain accepted and rejected attempts. Keep it as immutable
source evidence under `batches/`; per-attempt attributed events/alerts and native
results are stored under `accepted/` or `suspect/`. Do not analyze shared captures
as extra independent observations. A terminal interruption remains incomplete;
there is no implicit resume or substitution of prior observations.

## Retained legacy programs

`--cohort legacy` exercises every shipped pilot composite under the same bounded
replacement ledger. Linux can batch 16 distinct containers; Windows can batch
24 program/configuration slots. A legacy accepted run establishes successful
exit and valid collection/attribution only: those programs lack the expanded
suite's independent behavior assertions. Report them separately and never count
their exit status as proof that a target detection rule was qualified.
