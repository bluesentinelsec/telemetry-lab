# Repetition-count pilot (September 23, 2026)

This exploratory pilot is separate from the dissertation's confirmatory data. Release publication is deferred. Test programs and rules are the validated 0.3.0 draft bytes; support code is based on main `5b450a1` with the explicit pilot harness changes in this directory. All three Linux hosts use the same already validated patched Falco binary, and all Windows hosts must match the pinned Hayabusa/rule manifest. Inventories and hashes are retained.

## Matrix and units

Three independently provisioned Debian 13 / Windows Server 2025 lab pairs (A/B/C), c7i.xlarge. Each executes ten randomized repetition blocks, giving 30 planned observations per cell. Linux primitives: 13 x 8 configurations. Windows primitives: the currently implemented 3 x 6 configurations. Composites: 30 x 8 Linux and 23 x 8 qualified Windows cells, plus a same-binary control per active execution. Linux additionally has one negative baseline per configuration per block. The Windows onion diagnostic and retained legacy composites do not enlarge the qualified matrix.

The observation is one complete program execution, not an individual event. Runs remain nested in repetition blocks and hosts. Three hosts permit a preliminary check of host sensitivity, not a precise population-level estimate across cloud hosts. Warm-up is not subtracted by discarding startup events: every measured program starts as a fresh process. Initial measured runs remain visible. Fixture policy stays constant; ordinary Windows DNS cache is cleared before each DNS case as in the existing harness.

## Collection

Primitives use the shipped tmon and preserve raw telemetry, stderr, exit status, loss counters, hashes, event counts, and randomized plans. No duration filtering or outlier trimming is applied.

Linux composites retain a fresh isolated container for every active/control/baseline execution. Up to 16 idle containers are retained while Falco delivers events; one strict before/after health comparison covers the entire batch, including setup. Any counter increase or detector restart invalidates the whole batch. Events are assigned by exact container identity and event timestamp after that execution's start; pre-start fixture events are excluded. Raw journals remain unfiltered in the archive. Three seconds of post-batch draining and one second after cleanup separate batches. A preflight compares the selected-target outcomes with existing serial-runner evidence before full collection.

Windows uses the existing 30-second Sysmon drain, complete pinned Hayabusa replay, GUID-based attribution, and strict ambiguity checks. Local TCP and exact-name DNS fixtures are held constant while case and configuration orders are randomized. Active/control order is randomized. The existing RDP listener is used. No application-protocol libraries or external test endpoints are introduced.

Invalid attempts remain recorded. Only missing or invalid observations may receive separately identified replacements, preserving the initial and replacement attempt. Valid alert misses are never rerun to seek an alert. Report both valid-outcome repeatability and operational failure rate; do not erase invalid-run evidence.

## Decision criteria fixed before pilot collection

- Telemetry volume: target a 95% confidence-interval half-width <=5% of a positive raw mean. Estimate sample requirements from observed run-level variability; report within-host and pooled variation separately. Near-zero baseline-adjusted values require absolute uncertainty reporting, not division by zero.
- Event composition: use run-level event-type proportions with a target 95% interval half-width <=0.05 (5 percentage points). Syscall names and other event kinds define types; PIDs, timestamps and addresses do not create new types. Retain rare-event occurrence frequencies separately.
- Runtime contrasts: inspect matched repetition-block contrasts between the two configurations within each language and OS, including empty-adjusted volume. State a provisional 10% volume contrast as the effect-size planning target, 90% power, and show multiplicity/host-sensitivity limitations. Do not treat pilot significance as a confirmatory result.
- Composite repeatability: estimate alert probability per case/configuration and controls separately with exact binomial intervals. Sixty all-alerting observations give a one-sided 95% miss-rate upper bound below 5%; 100 reduce it below 3%. Mixed outcomes require additional rate-comparison planning and mechanism review, not an automatic cap at 60 or 100.
- The final recommendation is fixed before independent confirmatory collection. Preserve balanced counts within each planned runtime contrast. Do not claim the pilot's 30 runs establish absence of rare outcomes or a suite-wide reliability guarantee.

## Analysis and follow-up notes

`analyze.py ROOT OUTPUT --bundles RELEASE_DIRECTORY` reads archived executions, audits the full matrix against the original bundle manifests, computes pointwise run-level t intervals and exact binomial intervals, and exposes host means separately. Its SD-upper-bound sensitivity column assumes normal observations and is not a distribution-free guarantee, particularly for the Windows first-launch mixture. Power counts use a t/normal planning approximation for a 10% raw-volume contrast; they are not exact prospective power guarantees for arbitrarily small effects. No simultaneous-coverage claim is made across all cells.

`diagnostics.py ROOT OUTPUT` preserves primary results and adds explicitly exploratory first-versus-later-launch and cumulative-count tables. This diagnostic was added after observing the Windows first-launch pattern. It does not exclude those observations from the primary analysis or retrospectively redefine the precision target. If a future experiment changes the first-launch proportion, warm-up policy, sensor, ruleset, or implemented scope, its sampling plan needs review.

## Recorded pilot deviation: host B staging recovery

In Windows repetition 9, the C/MSVCRT PowerShell-profile control and active programs completed successfully, but the owned staged `probe.exe` remained before the next case. Subsequent batches correctly refused to overwrite it. The retained file matched the shipped C/MSVCRT PowerShell-profile executable; no process was running from that path. Its metadata, hash, and bytes were quarantined under the harness mutex. Twelve batches reported the stale-file guard; three additional batches encountered the mutex held during that recovery. The cleanup mechanism that left the file behind has not been established; it needs investigation before confirmatory collection.

All original evidence remains archived. Only these 15 failed batches receive replacements, in a separate `composites-replacements` directory, using the original per-batch seeds and plan. No test program, rule, measured process lifetime, or attribution criterion changes. The two executions from the incomplete first batch remain invalid under the existing whole-batch health gate. `analyze.py` retains initial failures in outcome totals and audits planned-slot coverage using explicitly identified replacements; it rejects replacement of any valid original outcome, including valid misses. Thus physical execution totals may exceed planned-slot totals without hiding duplicate attempts or failures.
