# Iteration threshold study — frozen before collection

## Question and scope
Compare 10,20,...,100 repetitions per test/configuration using measured event volume,
event composition, runtime contrasts and detection outcomes. No universal optimum
is assumed. These are exploratory planning data, separate from the final dissertation
experiment. Existing immutable 0.3.0 candidate programs, pinned rules and the prior
patched Falco build are reused; publication remains deferred.

Ten independent Debian 13 / Windows Server 2025 host pairs, c7i.xlarge. All existing
qualified cells: Linux primitives 13 x 8 configurations; Windows primitives 3 x 6;
Linux composites 30 x 8 plus paired controls and negative programs; Windows
composites 23 x 8 plus paired controls. DNS onion remains outside qualified scope.
Each host runs each cohort serially, with randomized test/configuration order.
No concurrent test process on a host. Network fixtures remain local.

## Sampling and validation
Record 21 complete repetition blocks per host/cohort. Block 1 is an explicit
first-launch diagnostic and is excluded from the primary subsequent-launch
sample-size comparison, but retained and reported. Every process still starts
and terminates normally: this does not exclude ordinary runtime startup/teardown.
For each host, the remaining 20 blocks are partitioned into 10 development and
10 validation blocks. Within each successive pair of blocks, a seeded coin flip
assigns one to each cohort. Thus development and validation span the same time
period, but no execution is shared. Assignment is frozen in allocation.json.
At n=10*k, take the first k development blocks from each of 10 hosts. Compare with
all 100 validation observations per cell. All 100 development observations are
physically collected; subsampling/bootstrap only measures sensitivity and is not
reported as additional executions. Host is the clustering unit; report within-host
and between-host variability, and uncertainty limited by ten independent hosts.

Planned physical observations per cell: 210 (10 initial,100 development,100 validation).
Planned primitive observations: 25,620; Linux composite observations:102,480;
Windows composite observations:77,280. Total:205,380.

## Prespecified analysis and decision
For every n report distribution across cells (median,95th percentile,maximum):
- Absolute relative error in mean event count versus validation.
- Total variation distance between mean per-run event-type proportions (not merely
  the largest individual event difference); new event types and their prevalence.
- Error in paired runtime mean contrasts, normalized by mean raw volume, plus
  sign agreement when the validation contrast is distinguishable from zero.
- Alert-rate error versus validation, change in alert/no-alert classification,
  discordant outcomes first discovered after each threshold, and unknown fraction.
- Measured collection duration and incremental cost in executions/time.

Show sensitivity at volume-error tolerances 1%,2%,5%,10% and composition distances
1,2,5 percentage points. These tolerances are policy choices, not statistical facts.
Report smallest n whose measured errors meet each tolerance for 95% and 100% of
cells and continue to do so at all later n; this is a descriptive observed stopping
point, not a guaranteed future bound. Use host-block bootstrap uncertainty and
randomized within-host subset sensitivity to show dependence on ordering.
Select a practical recommendation from measured tradeoffs and explain its chosen
accuracy target. If none is superior or some cells fail at 100, say so rather than
manufacturing an elbow. Report cohort-specific counts if warranted.

For binary outcomes, give exact pointwise binomial uncertainty under an explicit
independence assumption and host-level summaries. All-identical outcomes cannot
establish a unique optimal sample size: show probability of observing at least one
opposite outcome for hypothetical rates 1%,2%,5%,10%, at every n. Those rates are
sensitivity assumptions, not pilot observations. Do not equate zero observed misses
with zero miss probability, or use pseudo-replication to claim generality.

## Quality and integrity
Strict zero-drop collector health and existing process/container attribution stay
unchanged. Invalid/ambiguous records remain unknown, never misses. Missing slots
are explicit. No selective reruns of valid outcomes. If execution failure prevents
completion, retain original evidence and document any replacement separately;
primary analysis reports complete cases/available denominators and missingness.
First launches and all invalid attempts are preserved. No deletion of outliers.

Only harness cleanup is strengthened: verify removal of owned staged files after
target exit, retry up to ten seconds, then fail visibly. This addresses observed
silent failure of Remove-Item; it does not extend measured target lifetime or alter
rules, Sysmon settings, test source or binary. Preserve cleanup diagnostics.

Archive raw traces/events, commands, seeds, inventory, hashes, rules, health logs,
normalized data and analysis source. Verify remote/local archive SHA-256 before
teardown. Keep compressed raw archives; use one-host extraction at a time if local
space is limited. Destroy only this study's disposable resources after verification.

## Analysis clarification before inspecting new outcome estimates
After checking Chapter 3's planned endpoints, also assess empty-program-adjusted
runtime contrasts and paired runtime event-set Jaccard overlap. Collection and
allocation are unchanged. This clarification was made while only completion and
validity counts were being monitored, before computing new sample-size outcomes.
For adjusted contrasts, subtract each configuration's empty count in the same
host/repetition, then contrast runtimes; retain negative differences. Report both
error relative to raw volume and error relative to the validation contrast where
its host-level interval excludes zero. These are repeatability diagnostics, not a
claim of power for arbitrarily small effects. Raw event-type sets are compared
without inventing a set-subtraction analogue to numeric baseline adjustment.
