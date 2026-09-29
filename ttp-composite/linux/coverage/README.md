# Linux Falco coverage: standalone C, C++, Go, and Rust composites

Thirty standalone programs per language target 30 of the **95** supplied syscall rules in
upstream snapshot `e822409d8a2a28c9719f56ace66e8cadebfd2bc3`. All 30 are among
the 81 stock-enabled rules. The supplied collections contain 25 stable,
31 incubating, and 39 sandbox rules. `manifest.json` maps each case to its own
executable and exact target rule; `rule-inventory.csv` preserves selection and
exclusion rationale for all 95 rules.

The [shared behavior contract](behavior-contract.md) fixes each case's operation,
inputs, and required outcome for subsequent language ports.

## Standalone program contract

Each case has a separate `coverage/<case>/main.c` or `main.cpp` or `main.go`, build target, executable,
and hash. It runs its one behavior with no case-selection argument. There is
no `falco_cases` dispatcher, copied dispatcher, or shell wrapper. C (glibc/musl), C++ (libstdc++/libc++), Go (cgo/static), and Rust (static GNU/musl) builds install the programs under `<configuration>/coverage/` so they
do not overwrite the original seven-composite pilot.

Shared headers provide support functions. The three executable-loading cases
use one fixed benign helper to verify execution; the reverse-shell case uses
one fixed shell. These helpers do not select among test cases. Fixture setup
is a separate `fixture_prepare` program, outside the measurement window.

Every measured program also accepts `--control`: start the **same executable**
with the **same hash and path**, but skip its sole tested behavior. This is a
negative control, not a selector for another TTP. An additional standalone
`negative` program checks the common startup baseline. Active executions must
verify behavior and match their exact target rule; controls must not match any
of the 30 selected rules.

`verify_programs.py` checks the actual artifacts: complete roster, ELF format,
unique hashes, correct runtime loader, and absence of other cases' success
markers. For C++, it also checks the selected dynamic standard library and actual imported
library symbols. CI runs these checks for all eight implemented configurations. Release tests preserve every
program under its coverage subdirectory and reject accidental replacement of
legacy binaries. The broader primitive/composite audit is tracked in
[issue #55](https://github.com/bluesentinelsec/telemetry-lab/issues/55).

## C++ implementation and comparison

Clang++ and C++17 are held constant; the standard library varies between
libstdc++ and libc++. Both configurations use glibc. File streams perform
reads, writes, and truncation; `std::filesystem` performs links, rename,
directory creation, permission changes, and state checks. Streams retain their
default buffering. Paths, payloads, and success criteria match the C suite.
A fixed umask of 0077 gives new stream-created files/directories the same
0600/0700 permissions as the C fixtures.

C++17 has no standard socket, ptrace, fork/exec, or memfd API. Those behaviors
use native Linux/POSIX calls; helper-source reads use `std::ifstream`. Both
runtime builds use identical source. The fixed static C helper and shell are
shared across configurations. Every C++ executable uses the selected library
for control/success output; this does not imply every tested operation goes
through a C++ abstraction. The source documents which API is exercised, and
library internals may legitimately emit different syscalls. Linking alone is
not evidence that a particular behavior will produce a runtime difference.

## Go implementation and comparison

Each selected case has its own `coverage/<case>/main.go` package and binary.
The same Go compiler builds it with `CGO_ENABLED=1` and `CGO_ENABLED=0`.
As with the existing primitives, an explicit cgo-tagged linkage anchor ensures
that all cgo programs (including the baseline) really link glibc. No C function
performs the behavior. This axis changes runtime linkage/startup; it does not
imply that Go file or socket operations are delegated to libc. Artifact checks
require matching Go build metadata and dynamic/static ELF properties.

Go file operations use `os`; network operations use `net`; child execution uses
`os/exec`. Paths, payloads, and intended operations follow the shared mapping.
Linux-only socket/ptrace/memfd APIs use pinned `golang.org/x/sys/unix` v0.24.0.
The fixed static helper remains identical across all configurations.

Some implementation mechanisms differ and must be considered when
interpreting telemetry. A reverse shell uses `net.Conn` for standard streams,
so `os/exec` supplies pipes and copy goroutines. Command exchange and completion
are checked, but the unchanged socket-duplication rule may miss that execution.
Go also supports passing socket descriptors directly; this port deliberately
retains the existing Go pilot's pipe-relay approach. A resulting C/Go difference
is not evidence that cgo itself changes alert outcomes.
Memfd execution uses `ExtraFiles` and `/proc/self/fd/3` because Go has no standard
`fexecve` API. Ptrace operations lock the goroutine to its OS thread: attach
uses a disposable `/bin/sleep` child; TRACEME uses Go's pre-exec ptrace option and
the fixed helper. C uses fork-only children for those tracing cases. These are
explicit language implementation choices, not evidence of runtime causation by
themselves. Both Go configurations use identical source and child fixtures.

A valid miss is preserved. The runner still requires all selected targets to
be demonstrated somewhere in the selected run; include the C reference rather
than changing a Go implementation or target rule just to make that gate pass.

## Rust implementation and comparison

Each selected case has its own `coverage/<case>/main.rs` and Cargo binary target.
Rust 1.98.1 and the same source are held constant across
`x86_64-unknown-linux-gnu` and `x86_64-unknown-linux-musl`; both use static CRT
linking, following the existing Rust matrix. The pinned `libc` crate (0.2.177)
provides bindings for native APIs; it is not the linked C runtime itself.
GNU links the build host's static glibc; musl links the target toolchain's
bundled static musl. Their target-specific Rust standard libraries also differ,
so this compares target/runtime configurations rather than isolating libc alone.
The compiler, target libraries, and executable hashes must be frozen for the
final experiment. Artifact verification requires static ELF properties, a
compile-target marker, and actual GNU/musl startup symbols, not just filenames.

File behavior uses `std::fs`, `OpenOptions`, and Unix permission/link extensions.
Networking uses `std::net`; child execution uses `std::process::Command`.
The reverse shell retains the existing Rust pilot's direct `TcpStream` to
`OwnedFd` to `Stdio` conversions, with the same shell command and checked reply
as C/C++/Go. Rust's memfd case uses a native memfd plus `Command` execution
through `/proc/self/fd/`, because std has no `fexecve` interface. The memfd is
kept open across exec and the exact fixed helper output is checked.

The packet socket and ptrace cases use explicit native APIs through `libc`.
Ptrace uses fork-only disposable children, matching the C fixtures. No Rust
threads are started in those binaries before fork, and the child uses only
native calls before `_exit` or its pause loop. This avoids disguising a child
exec/startup difference as a ptrace/runtime effect. Both Rust configurations
use identical behavior, paths, payloads, helper, and independent checks.
Standard-library bookkeeping and verification may still emit different events;
valid misses and additional rule matches remain research data.

## Requirements and containment

Use the project's disposable Debian 13 x86-64 EC2 lab with Docker and Falco.
Rustup must provide the pinned Rust toolchain and both Linux targets; SSM
sessions should set explicit `CARGO_HOME`, `RUSTUP_HOME`, and cargo `PATH`.
The programs require a Docker fixture environment. The runner creates a fresh
container with no external networking for each execution. Metadata-service
and UDP peers are sockets in that container's private network namespace;
no real metadata service, credentials, or external target is contacted.

The fixed configuration adds NET_ADMIN and SYS_PTRACE, retains NET_RAW, uses
an unconfined seccomp profile for the exercised syscalls, and makes the private
/dev/shm mount executable. Containers are not privileged and have no host
filesystem mounts. Files are synthetic or confined to the disposable layer;
container removal cleans them up. No persistence fixture is activated.

## Collector health

Falco 0.45.0 uses a [pinned libsinsp parser fix](falco-health-fix/README.md) for partially populated syscall-entry events. Setup builds and tests it on the lab host, preserves the packaged detector, and records the actual running binary and build receipt. Detection rules and strict health checks remain unchanged.

## Deploy and run

Deploy through the existing infrastructure:

```sh
cd lab-environment
npm ci
npx cdk deploy -c linuxOnly=true -c stackName=FalcoCoverageValidation
```

Stage repository source on the host through S3 and SSM. After cloud-init,
install dependencies and run from the staged repository root:

```sh
sudo apt-get update
sudo apt-get install -y gcc make cmake musl-tools libc6-dev python3-yaml \
  clang libc++-dev libc++abi-dev binutils golang
bash ttp-composite/linux/coverage/build.sh /opt/lab/standalone-build
sudo bash ttp-composite/linux/coverage/setup-detector.sh
sudo python3 ttp-composite/linux/coverage/run.py \
  --output /opt/lab/standalone-results --repetitions 3 --seed 20260921
```

The same image contains all eight C, C++, Go, and Rust configurations. A repetition schedules
**488 executions**: 30 active programs and 30 same-binary controls per
configuration, plus eight baselines. Three repetitions schedule 1464.
To validate just C++ (122 executions per repetition), add
`--config linux-cpp-libstdcxx --config linux-cpp-libcxx`. The selected
configurations are recorded in provenance. For a Go qualification with a C
reference under the same image and host, use `--config linux-c-glibc
--config linux-go-cgo --config linux-go-static` (183 executions per repetition).
For Rust with the same C reference, use `--config linux-c-glibc
--config linux-rust-gnu --config linux-rust-musl` (also 183 executions).
Each block is randomized. `--case ID` restricts a diagnostic run and includes
that case's control; it does not validate the complete selection.

The dedicated detector loads only the three preserved rule files, evaluates
all matches, and emits one stdout JSON stream. It leaves rule logic, exceptions,
macros, lists, and enabled flags unchanged. Restore the normal lab service
when reusing the host:

```sh
sudo systemctl stop falco-coverage.service
sudo systemctl start falco-modern-bpf.service
```

## Evidence and interpretation

A behavior succeeds only after checking outputs, data transfer, file state,
or child completion and printing its exact success marker. Alerts are scoped
to the fresh container and journal window and matched by exact rule name.
The runner rejects failed behavior, detector restarts, counter resets, and
increases in any captured drop counter. Invalid attempts remain in the data.
A healthy, successful behavior with no target alert remains a valid miss.

`qualified_case_configurations` requires both a valid target hit and a valid,
clean same-binary control for each case/runtime pair. A value of 60 documents positive/control evidence for all programs in the two
selected configurations (240 if all eight configurations demonstrate positives). It is descriptive, not an inclusion requirement: a valid
miss in another runtime remains research data once the target rule has been
demonstrated. The process exits nonzero if a target has never been demonstrated,
any scheduled attempt is invalid, or any negative control fails. Rechecks
must be retained alongside the original attempts, not silently substituted.

The controls test whether startup of the program alone triggers a selected
rule. They do not prove the rules are independent of paths, process names, or
command lines: such event fields are legitimate predicates in several stock
rules. Inspect rule conditions and the alert's event fields before attributing
a future difference to runtime. These Falco syscall rules do not constitute a
static binary-scanning experiment.

Thirty rules are not thirty independent mechanisms. The two metadata targets
share a behavior, and other rules overlap. Preserve non-target matches as
observations without redefining the declared target coverage.

Output includes every program's hash, image ID, randomized plan, behavior and
control output, exact-rule alerts, journal windows, and collector metrics.
`--functional-only` does not claim detection qualification. Preserve the raw
archive before tearing down the disposable stack.

```sh
python3 -m unittest discover -s ttp-composite/linux/coverage -p 'test_*.py' -v
```

C results are under `validation/`; C++ results are under `validation/cpp/`; Go results are under `validation/go/`; Rust results are under `validation/rust/`. Earlier dispatcher-based results are
retained under `validation/dispatcher-pilot/` solely as historical evidence;
they do not validate these replacement executables. Other language ports,
Windows coverage, and paired telemetry-analysis integration remain in
[issue #54](https://github.com/bluesentinelsec/telemetry-lab/issues/54).

## Collector health metrics

The lab reads cumulative health counters through Falco's Prometheus endpoint.
`setup-detector.sh` disables periodic metrics-as-alert and metrics-file output,
leaving Prometheus as the sole metrics reader. In Falco 0.45.0, periodic output
and HTTP scrapes can concurrently reset and sum libpman's shared statistics
buffer, making a cumulative event counter appear to decrease even though the
collector process has not restarted. Strict health checks reject such snapshots.
The correction removes the competing reader; it does not suppress detector
alerts, change rules, ignore drop counters, or relax the health gate.

Native qualification uses repeated serial HTTP scrapes with periodic output
enabled, disabled, re-enabled, and disabled again, followed by complete
composite/legacy preflights and an injected collector-stop recovery check.
Keep those diagnostics separate from the 200-repetition validation dataset.
