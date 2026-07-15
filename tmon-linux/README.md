# tmon-linux

`tmon` (telemetry monitor) is a process-scoped syscall tracer for Linux, built on
eBPF/libbpf CO-RE. It spawns a target program, follows its entire process tree
from birth, and records every system call — with decoded arguments and return
values — human-readable by default, or JSONL for machine consumption. It is the
Linux half of the telemetry-lab study's monitor; the Windows counterpart (ETW)
shares the `tmon` name as a separate project.

Think `strace`, but scoped by a kernel-side BPF filter rather than ptrace, so the
target runs at native speed and unrelated processes are never even copied out of
the kernel.

## How it works

1. `fork()` the target and stop it (`SIGSTOP`) before it `execve`s.
2. Seed a BPF hash map with the child's tgid, so the filter is armed *before* the
   target runs a single instruction.
3. `SIGCONT` the target. From here every syscall it (or any descendant) makes is
   captured via `raw_syscalls:sys_enter` / `sys_exit`.
4. `sched_process_fork` grows the traced set to cover new children (unless
   `--no-follow`); `sched_process_exec`/`exit` bound the tree.

Each syscall is captured as an enter record (arguments) and an exit record
(return value); the two are paired per thread into one row carrying the args, the
result, and the wall-clock **duration**. Pointer arguments (file paths,
sockaddrs) are decoded **at exit**, when the kernel has already faulted the page
in, so decoding is reliable rather than best-effort; the exec path is taken from
the `sched_process_exec` tracepoint's own filename field. Records are emitted
variable-length, so the path buffer only costs ring space when a path is present
— which keeps dropped events at zero even under heavy syscall load.

## Quick start

```sh
# Build (see "Building" for dependencies)
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build

# Loading BPF needs root (or CAP_BPF + CAP_PERFMON):
sudo ./build/tmon -- /bin/echo hello
sudo ./build/tmon --format json -o run.jsonl -- ./my-primitive
```

## User guide

### Options

```
tmon [options] -- <program> [args...]
tmon [options] <program> [args...]        # the -- is optional

  -f, --format human|json   Output format (default human; json is JSONL)
  -o, --output FILE         Write to FILE instead of stdout
  --no-decode               Do not decode pointer args (paths, sockaddrs); on by default
  --no-returns              Do not capture return values (skip sys_exit)
  --no-follow               Do not follow fork/exec descendants
  -c, --summary             Suppress the per-event stream; print only the summary
  -q, --quiet               Suppress the trailing summary line
  -n, --max-events N        Stop after N syscall events (0 = unlimited)
  --buffer-mb N             Ring-buffer size in MiB (default 64); raise if events drop
  --meta KEY=VALUE          Attach metadata to machine-readable output (repeatable)
  --version, -h/--help
```

Decoding and return-value capture are **on by default**: they are passive
kernel-side reads that do not change the target's behavior. Turn them off only to
minimize tracer overhead. `tmon` exits with the target's own exit code, so it is
transparent in a pipeline.

### Common invocations

```sh
tmon -- ./primitive                    # human-readable trace to the terminal
tmon ./primitive arg1 arg2             # same, bare form (no --)
tmon --format json -o run.jsonl -- ./primitive     # JSONL to a file
tmon -c -- ./primitive                 # just the summary (counts + exit code)
tmon --no-follow -- ./primitive        # ignore child processes
tmon -n 1000 -- ./primitive            # cap at 1000 syscalls
tmon --buffer-mb 256 -- ./primitive    # bigger ring for very high syscall rates
tmon --meta lang=c --meta build=musl --format json -o run.jsonl -- ./primitive
```

### Example: tracing a specimen

The repo ships a small specimen (`examples/specimen.c`) that writes and reads a
file, opens a socket and connects to a closed port (a deliberate failure), and
spawns a subprocess:

```sh
cc -O2 -o specimen examples/specimen.c
sudo tmon -- ./specimen
```

Human output (excerpt) — note decoded paths, the decoded sockaddr, `= result`,
the errno symbol on failure, and the `<seconds>` duration:

```
   0.000000 19805  specimen   +++ exec "/root/specimen" (now specimen) +++
   0.001570 19805  specimen   openat(0xffffff9c, "/tmp/tmon-specimen.dat", 0x241, 0x1a4, ...) = 3 <0.000010>
   0.001582 19805  specimen   write(0x3, 0x55c52640a01b, 0xe, ...) = 14 <0.000004>
   0.001588 19805  specimen   openat(0xffffff9c, "/tmp/tmon-specimen.dat", 0x0, ...) = 3 <0.000001>
   0.001590 19805  specimen   read(0x3, 0x7ffe42bd0250, 0x40, ...) = 14 <0.000001>
   0.001593 19805  specimen   socket(0x2, 0x1, 0x0, ...) = 3 <0.000007>
   0.001602 19805  specimen   connect(0x3, 127.0.0.1:9999, 0x10, ...) = -111 ECONNREFUSED(111) <0.000054>
   0.001731 19805  specimen   +++ fork -> child 19806 +++
   0.001993 19806  echo       +++ exec "/bin/echo" (now echo) +++
   0.002534 19806  echo       write(0x1, 0x5585ab701b60, 0x11, ...) = 17 <0.000003>
   0.002583 19806  echo       +++ exited with 0 +++
   0.002658 19805  specimen   +++ exited with 0 +++
tmon: 157 syscalls (16 failed), 162 events, 2 process(es), 0 dropped; target exit 0
```

The same run as JSONL (`--format json`), one object per line:

```json
{"record":"meta","tool":"tmon","command":["/root/specimen"],"meta":{"lang":"c"}}
{"record":"event","kind":"syscall","ts_ns":27786355297223,"pid":17819,"tid":17819,"comm":"specimen","nr":257,"syscall":"openat","args":["0xffffffffffffff9c","0x5631782ff004","0x241","0x1a4","0x0","0x0"],"path":"/tmp/tmon-specimen.dat","path_argno":1,"ret":4,"ok":true,"duration_ns":12619}
{"record":"event","kind":"syscall","ts_ns":27786355342180,"pid":17819,"tid":17819,"comm":"specimen","nr":42,"syscall":"connect","args":["0x4","0x7ffe33cc6fc0","0x10","0x0","0x0","0x0"],"sockaddr":"127.0.0.1:9999","sockaddr_argno":1,"ret":-111,"ok":false,"error":"ECONNREFUSED","errno":111,"duration_ns":83669}
{"record":"event","kind":"exec","ts_ns":27786355720963,"pid":17820,"tid":17820,"comm":"echo","path":"/bin/echo"}
{"record":"event","kind":"fork","ts_ns":27786355489673,"pid":17819,"comm":"specimen","child_pid":17820}
{"record":"event","kind":"exit","ts_ns":27786356327399,"pid":17820,"comm":"echo","exit_code":0}
{"record":"summary","syscall_events":157,"failed_syscalls":16,"total_events":162,"processes":2,"dropped":0,"target_exit_code":0}
```

### JSONL schema

Every line carries a `record` discriminator:

| record | fields |
|---|---|
| `meta` | `tool`, `command` (argv array), `meta` (your `--meta` key/values) |
| `event` | `kind` ∈ {`syscall`,`fork`,`exec`,`exit`}, `ts_ns`, `pid`, `tid`, `comm`, plus per-kind fields below |
| `summary` | `syscall_events`, `failed_syscalls`, `total_events`, `processes`, `dropped`, `target_exit_code` |

Per-kind `event` fields:

| kind | fields |
|---|---|
| `syscall` | `nr`, `syscall` (name), `args` (6 hex strings), optional `path`/`path_argno`, optional `sockaddr`/`sockaddr_argno`, and when returns are captured: `ret`, `ok` (bool), `error`+`errno` on failure, `duration_ns` |
| `fork` | `child_pid` |
| `exec` | `path` (full executable path) |
| `exit` | `exit_code` |

Syscall args are hex strings so full 64-bit values survive JSON; `ts_ns` is
boot-time monotonic nanoseconds (good for ordering and intervals).

### Completeness

If a run reports non-zero `dropped`, the ring buffer overflowed and some events
were lost — raise `--buffer-mb`, or reduce load with `--no-decode`/`--no-returns`.
In practice the default 64 MiB buffer sustains six-figure syscall bursts with zero
drops (e.g. `ls -laR /usr`, ~139k syscalls). The counter is always reported, so a
clean run is provably complete.

## Source layout (three layers)

| Layer | Directory | Responsibility |
|---|---|---|
| 1 — data model | `src/model/` | Plain value types: `Event`, `Config`. |
| 2 — business logic | `src/core/` | Capture `Engine`, `EventSink`, syscall/errno names, wire→domain decode, `--meta` parse. Owns all OS/BPF machinery. |
| 3 — presentation | `src/view/` | `HumanFormatter` and `JsonFormatter`, both `EventSink`s. |
| BPF (kernel) | `bpf/` | `tmon.bpf.c` CO-RE program + `tmon_event.h` wire format shared with the engine. |
| CLI | `cli/main.cpp` | The only place the three layers are wired; the only CLI11 consumer. |

## Building

Requires a Linux host with BTF (`/sys/kernel/btf/vmlinux`) — Debian 13 has it.

```sh
apt-get install -y clang llvm bpftool libbpf-dev libelf-dev zlib1g-dev \
    cmake ninja-build git pkg-config
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

CLI11 and cJSON are fetched and compiled in (pinned tags); the build also
generates `vmlinux.h` from the host BTF, compiles the BPF object, generates the
libbpf skeleton, and builds the syscall-name and errno tables from the host's
`<asm/unistd_64.h>` and `<asm-generic/errno*.h>`.

### Dependency strategy

`libbpf` is statically linked (a bare Debian host is unlikely to have it).
`glibc` stays dynamic; `libelf`/`libz` are dynamic too — static `libelf.a` on
Debian drags in unpackaged elfutils-internal symbols, and both shared libs are
either universal (zlib) or a one-package install (`libelf1`). `libstdc++`/`libgcc`
are statically bound; CLI11 and cJSON are compiled in. The result is a ~3 MB
binary whose only runtime needs are glibc, `libelf1`, `zlib1g`, and `libzstd1`.

## Tests

The kernel-independent logic lives in a `tmon_core` static library covered by a
Catch2 unit suite (syscall/errno resolution, wire→domain decode incl. sockaddr,
both formatters, `--meta` parsing):

```sh
cmake --build build
ctest --test-dir build --output-on-failure
```

The BPF engine (spawn-and-trace, verifier, ring buffer) needs a real kernel and
root, so it is exercised by running `tmon` on a live host rather than unit-tested.
CI (`.github/workflows/build-tmon.yml`) builds everything and runs the suite in a
`debian:trixie` container on every change under `tmon-linux/`. Disable the tests
in a build with `-DTMON_BUILD_TESTS=OFF`.

## Status

Implemented: from-birth tree-scoped capture; per-syscall arguments, return values,
errno, and duration; decoded file paths and sockaddrs; human + JSONL output; drop
accounting; `-o`, `--meta`, `--no-follow`, `--no-decode`, `--no-returns`, `-c`,
`-n`, `--buffer-mb`. Argument decoding currently covers path- and sockaddr-bearing
syscalls; scalar flag decoding (e.g. `open` flags) and syscall-family excludes are
planned follow-ups.
