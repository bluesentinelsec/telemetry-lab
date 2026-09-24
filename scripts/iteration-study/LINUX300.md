# Linux 300-repetition replication

The `*300.py` drivers run the Linux-only replication. The unsuffixed
`orchestrate.py`, `watch.py`, `finalize.py`, and neighboring protocol/allocation
files belong to the earlier Linux/Windows 100-repetition study. Do not use those
drivers to provision or destroy this replication.

The authoritative pre-collection protocol and allocation are archived in:

`/Users/michaellong/telemetry-lab-data/linux-300-study-2026-09-24/`

That directory contains `PROTOCOL.md`, `allocation.json`, `study.json`, their
digests, immutable input archives, full per-host evidence, and analysis results.
Twenty Linux hosts each run 31 randomized blocks: one initial-launch block and
15 development / 15 validation blocks allocated within chronological pairs.
This gives 300 development and 300 separate validation observations per cell.
All 367,040 planned native executions must be reconciled before completion.

## Analysis reproduction

Use the Python/numpy/scipy versions recorded in `python-environment.json` and
matplotlib 3.11.2 for plotting. Extract the archived Linux release bundle beneath
a directory and set `TELEMETRY_STUDY_BUNDLES` to that parent directory. The
normalizer checks native hashes against the extracted immutable bundle.

Pass the archived study directory as the sole argument to these scripts:

1. `normalize.py` (one compressed host archive at a time)
2. `audit.py` and `provenance.py`
3. `analyze.py` (500 resamples by default)
4. `diagnostics.py` and `composite_diagnostics.py`
5. `plateau.py` and `dependence300.py`
6. `report300.py` and `plot300.py`

`normalize.py` skips hosts with existing verification files. Reproduce in a copy
without `normalized/` and `analysis/` to force verification from the raw archives;
preserve the original archive receipts, protocol, allocation, and input files.
Rules are verified against the corresponding archived source revision.

`test_analysis.py` covers the old and new host/count designs, a deliberately late
opposite detection outcome, unknown-outcome denominators, and control alerts on
selected rules other than their paired target. Synthetic data are never included
in measured results. `scripts/pilot/test_collector_guard.py` exercises durable
evidence and frozen-collector recovery; every study host also performs a real
recovery preflight before measurement.

`finalize300.py` requires complete analyzed data and an `ANALYSIS_REVIEWED` marker,
rechecks raw hashes and exact slots, archives remote logs/source/infrastructure,
then destroys only `Linux300Study20260924`. It verifies all twenty study instances
terminated and their volumes disappeared. It does not publish a release or push
anything to GitHub.
