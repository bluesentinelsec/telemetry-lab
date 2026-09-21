# Linux Falco coverage: C qualification suite

Thirty explicitly mapped cases target 30 of the **95** syscall rules in the
preserved upstream snapshot (`e822409d8a2a28c9719f56ace66e8cadebfd2bc3`). All 30
are among the 81 stock-enabled rules. The collection counts are 25 stable,
31 incubating, and 39 sandbox. `manifest.json` is authoritative for case IDs,
target names, source hashes, and C configurations; `rule-inventory.csv` records
the proposed selection/exclusion rationale for all 95 rules. That CSV retains
the original source-review status; execution evidence comes from run outputs.

The suite implements the entire selection in C, built with GCC against glibc
and musl. It complements the existing seven-composite, four-language pilot;
the additional cases are not yet implemented in C++, Go, Rust, or Windows.
Thirty rules are not thirty independent detection mechanisms: some overlap,
and the two metadata targets deliberately share the same behavior.

## Requirements and containment

Use the project's disposable Debian 13 x86-64 EC2 lab with Docker and Falco.
Do not run these fixtures directly on a workstation or production host.
The C executable refuses execution outside a Docker container or without the
fixture environment marker. The runner creates a fresh container per execution
with no external networking. Both metadata-service and UDP peers are sockets
inside that container's own network namespace; no real metadata service,
credential source, or external target is contacted.

The fixed container configuration adds NET_ADMIN (loopback address setup) and
SYS_PTRACE, retains Docker's NET_RAW capability, permits the exercised syscalls
with an unconfined seccomp profile, and makes a private /dev/shm mount executable.
These settings are identical across both runtime configurations. The container
is not privileged and has no host filesystem mounts. Files are synthetic or
confined to its disposable writable layer. No persistence fixture is activated.

## Deploy and build

Deploy a Linux-only instance using the existing infrastructure:

```sh
cd lab-environment
npm ci
npx cdk deploy -c linuxOnly=true -c stackName=FalcoCoverageValidation
```

Stage the repository source on that host through the stack's data bucket and
SSM. After cloud-init finishes, install build dependencies:

```sh
sudo apt-get update
sudo apt-get install -y gcc make cmake musl-tools libc6-dev python3-yaml
bash ttp-composite/linux/coverage/build.sh /opt/lab/falco30-build
sudo bash ttp-composite/linux/coverage/setup-detector.sh
sudo python3 ttp-composite/linux/coverage/run.py \
  --output /opt/lab/falco30-results --repetitions 3 --seed 20260921
```

`build.sh` verifies different ELF interpreters and compiles one identical static
helper for both variants. The calling test program performs the operation under
comparison natively. The fixed helper only confirms successful execution in
the three executable-loading cases. The reverse-shell case uses the same shell
and checks a fixed command/response exchange through its redirected descriptors.

The dedicated `falco-coverage.service` loads only the preserved rule files;
upstream auto-update files do not affect it. It uses `rule_matching: all` and a
debug output threshold while leaving rule conditions, exceptions, macros,
lists, and stock enabled flags unchanged. It stops the normal lab Falco service
to avoid two collectors competing. Restore normal operation when done:

```sh
sudo systemctl stop falco-coverage.service
sudo systemctl start falco-modern-bpf.service
```

## Execution and interpretation

Each repetition block randomly orders the 30 cases and the negative control
across both configurations: **62 executions per block**, 186 for three blocks.
The manifest and randomized order are saved before execution. `--case ID` can
restrict a diagnostic run, but such a run does not qualify the entire suite.

Fixture preparation is a separate process before a journal cursor is recorded.
The measured process must return zero and print its exact `CASE_OK` marker only
after checking outputs, data transfer, file state, or child completion.
Falco alerts are attributed by the fresh container's ID and capture window.
The target must match the exact manifest rule name; another alert cannot
substitute. Other attributable rules are retained as descriptive observations.

The runner checks that the detector stayed active with the same PID, that
kernel event/drop counters did not reset, and that drop counters did not rise.
Behavior failures and collector failures are invalid runs, never evidence of
a detection miss. A successful behavior with a healthy detector and no target
match remains a valid negative detection outcome. The empty control must not
match any of the 30 selected rules.

`summary.json` reports the number of distinct target rules observed on valid
runs. It does not require every runtime to alert, because that would exclude
the runtime-induced differences the study seeks to measure. Review the per-run
matrix before interpreting a no-alert outcome as runtime-related. These runs
qualify fixtures and feasibility; they are not the dissertation's 30-repetition
confirmatory dataset or validation of the six unimplemented non-C variants.

Each output directory includes provenance, planned order, behavior stdout and
stderr, attributed alert JSON, original journal records, and before/after
collector metrics. Preserve this evidence before destroying the temporary
stack. Raw journal records include other host activity and should be reviewed
before sharing; the curated validation summary contains only scope/results.

`--functional-only` exercises behavior without claiming detection validation.
It records `collection_ok=false`, so those records cannot be confused with
qualified rule outcomes.

## Checks

```sh
python3 -m unittest discover -s ttp-composite/linux/coverage -p 'test_*.py' -v
```

Tests guard against wrong-rule substitution, unrelated-container alerts,
failed behavior being counted as a detection, collector restarts/drops,
negative-control contamination, and changes to the pinned rule corpus.

See `validation/README.md` for the recorded live-lab qualification outcome.
