# Windows onboarding checkpoint — 2026-10-08

Paused at the user's request. Implementation is ready for live qualification;
**no new case has yet been qualified against Sysmon/Hayabusa in the AWS lab**.
Keep the qualified Windows count at 52. There are now 56 implemented candidates.
Do not merge or update the qualified count until the remaining work passes.

## Completed

- Four standalone cases in C, C++, Go and Rust: `unicode_child_arguments`,
  `ads_provenance_contents`, `raw_owned_volume_read`, and
  `signed_system_library_load`. All retain same-binary no-behavior controls.
- Original stock predicates and rule hashes added to selection.json, with
  `pending-live-qualification` status. Detector rules/profile are unchanged.
- Owned read-only VHD fixture, exact Unicode helper receipt, stream readback,
  system-library provenance, and harness setup/cleanup.
- CI run [37804625569](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/37804625569)
  passed all 17 jobs, including all eight Windows native behavior/build checks,
  at source `20dcae9`.
- Subsequently changed C++ stream-content I/O from stdio to fstreams so it
  exercises the selected C++ standard library. Rebuild
  [37805868992](https://github.com/bluesentinelsec/telemetry-lab/actions/runs/37805868992)
  passed all 17 jobs at source `2726bac`, including all eight Windows configurations.
- Local Windows evidence tests: 26 passed; expansion tests: 2 passed;
  experiment tests: 22 run, one skipped; CDK build and 22 infrastructure tests
  passed. Go cross-build of all four additions passed.
- Code and assessment are pushed to `feat/windows-coverage-expansion`.

## AWS and evidence state

Default AWS credentials authenticate successfully. The configured default region
is us-west-2, so **explicitly use us-east-1** for every lab action.

- CDK stack: `WindowsExpansionQualification`, deployed Windows-only.
- Instance: `i-0fe6a26a00f1eec3e`, c7i.xlarge, Windows Server 2025, us-east-1b.
- Instance confirmed **stopped** at the pause; start it before resuming.
- Local evidence root: `/Users/michaellong/telemetry-lab-data/windows-expansion-2026-10-08`.
- Stack outputs: `outputs.json` under that root. Deployment logs, CI metadata,
  and the first CI run's eight Windows artifacts are also there.
- No staging command, detector run, or qualification campaign has been submitted.
- EC2 system/instance checks passed, but Systems Manager had not registered at
  the pause. Bootstrap completion is unknown. Check inventory, Sysmon service,
  and Defender removal after restart. If bootstrap was interrupted and cannot
  resume cleanly, recreate only this disposable task stack via CDK.
- Initial us-east-1a deployment failed for capacity. A concurrent retry briefly
  hit the VPC limit during rollback. Both failed stacks were cleaned up; only
  the successful task stack remains. Use us-east-1b for recreation.
- Existing historical raw data was not moved, copied, or uploaded. New CI
  binaries/evidence stay outside Git. Stopped EBS storage remains allocated.

## Resume

1. Check CI 37805868992. Start the instance in us-east-1, wait for SSM, and
   verify `C:\lab\inventory.json`, running Sysmon64, and absent Defender.
   Diagnose/recreate bootstrap if needed; do not stage over unfinished setup.
2. Stage the final successful CI artifact set using the existing launcher:

   ```sh
   python3 scripts/coverage-expansion/lab.py stage \
     --evidence /Users/michaellong/telemetry-lab-data/windows-expansion-2026-10-08 \
     --outputs /Users/michaellong/telemetry-lab-data/windows-expansion-2026-10-08/outputs.json \
     --stack WindowsExpansionQualification --os windows --phase stage \
     --ci-run 37805868992
   ```

   Check staging status; this pins Hayabusa and verifies all rule hashes.
3. Run a one-repetition C UCRT reference pilot for the four new cases using
   `lab.py run`, a fresh phase, `--config windows-c-ucrt`, the four repeated
   `--case` options, `--repetitions 1`, and `--no-retry`. Collect and analyze
   the actual evidence before admitting candidates. Preserve valid misses and
   failed attempts; never weaken predicates to make them alert.
4. After reference qualification, run all eight configurations, three
   repetitions per active/control mode: 192 planned observations for four
   cases. Preserve attribution/health failures separately under the normal
   replacement policy. Also run helper-dependent regressions, at least
   `double_extension_execute` and `ads_executable`, because helper bytes changed.
5. Collect the full raw archive locally, verify remote/local bytes, and record
   hashes and compact per-case/configuration results in the PR. Review raw
   target fields, helper and disk-cleanup receipts, library signature/hash,
   exact rule IDs, and clean controls. No live result is implied by CI behavior.
6. Update selection qualification, scope counts, inventories, and documentation
   only for accepted candidates. Correct the existing Windows README's 12-event
   statement (the original 52 rules permit 16 event IDs; the raw-read candidate
   would add event 9). Historical datasets keep their original counts.
7. Finish the draft PR, run required CI, and leave it ready for review. Once new
   raw evidence is verified locally, tear down this disposable CDK stack.

The detailed behavior/API contract is in
[expansion-2026-10.md](../../ttp-composite/windows/coverage/expansion-2026-10.md).
Linux implementation and lab testing are outside this task.
