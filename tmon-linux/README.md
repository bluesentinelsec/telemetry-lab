# tmon-linux

`tmon` (telemetry monitor) is a process-scoped syscall tracer for Linux, built on
eBPF/libbpf CO-RE. It spawns a target program, follows its entire process tree
from birth, and emits every system call — human-readable by default, or JSONL for
machine consumption. It is the Linux half of the telemetry-lab study's monitor;
the Windows counterpart (ETW) shares the `tmon` name as a separate project.

Think `strace`, but scoped by a kernel-side BPF filter rather than ptrace, so the
target runs at native speed and unrelated processes are never even copied out of
the kernel.

## How it works

1. `fork()` the target and stop it (`SIGSTOP`) before it `execve`s.
2. Seed a BPF hash map with the child's tgid, so the filter is armed *before* the
   target runs a single instruction.
3. `SIGCONT` the target. From here every syscall it (or any descendant) makes is
   captured via the `raw_syscalls:sys_enter` tracepoint.
4. `sched_process_fork` grows the traced set to cover new children (unless
   `--no-follow`); `sched_process_exec`/`exit` bound the tree.

Scoping in the kernel — not by post-filtering in user space — means the ring
buffer only ever carries events that belong to the target's tree.

## Source layout (three layers)

| Layer | Directory | Responsibility |
|---|---|---|
| 1 — data model | `src/model/` | Plain value types: `Event`, `Config`. No behavior. |
| 2 — business logic | `src/core/` | Capture `Engine`, `EventSink` interface, syscall-name resolution. Owns all OS/BPF machinery. |
| 3 — presentation | `src/view/` | `HumanFormatter` and `JsonFormatter`, both `EventSink`s. |
| BPF (kernel) | `bpf/` | `tmon.bpf.c` CO-RE program + `tmon_event.h` wire format shared with the engine. |
| CLI | `cli/main.cpp` | The only place the three layers are wired together; the only CLI11 consumer. |

The dependency arrow points inward: the engine depends on the `EventSink`
abstraction, never on a concrete formatter.

## Usage

```
tmon [options] -- <program> [args...]
tmon [options] <program> [args...]     # the -- is optional
```

| Option | Meaning |
|---|---|
| `-f, --format human\|json` | Output format (default `human`; `json` is JSONL). |
| `-o, --output FILE` | Write to FILE instead of stdout. |
| `--decode` | Resolve pointer/flag arguments (raw args always emitted). *(reserved for a later increment)* |
| `--no-follow` | Do not follow fork/exec descendants. |
| `-c, --summary` | Suppress the per-event stream; emit only the summary. |
| `-q, --quiet` | Suppress the trailing summary line. |
| `-n, --max-events N` | Stop after N syscall events (0 = unlimited). |
| `--meta KEY=VALUE` | Attach metadata to machine-readable output (repeatable). |

`tmon` exits with the target's own exit code, so it is transparent in a pipeline.

### JSONL records

Every line carries a `record` discriminator:

- `meta` — one preamble line (tool, command, any `--meta`).
- `event` — one per captured action; `kind` is `syscall`/`fork`/`exec`/`exit`.
  Syscall args are hex strings so full 64-bit values survive JSON.
- `summary` — one trailer line with counts and the target exit code.

## Building

Requires a Linux host with BTF (`/sys/kernel/btf/vmlinux`) — Debian 13 has it.

Build dependencies:

```sh
apt-get install -y clang llvm bpftool libbpf-dev libelf-dev zlib1g-dev \
    cmake ninja-build git pkg-config
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

CLI11 and cJSON are fetched and compiled in (pinned tags); the build also
generates `vmlinux.h` from the host BTF, compiles the BPF object, generates the
libbpf skeleton, and builds the syscall-name table from the host's
`<asm/unistd_64.h>`.

## Tests

The kernel-independent logic lives in a `tmon_core` static library — syscall-name
resolution, wire→domain decoding, both formatters, and `--meta` parsing — and is
covered by a Catch2 unit suite:

```sh
cmake --build build
ctest --test-dir build --output-on-failure
```

The BPF engine (spawn-and-trace, verifier, ring buffer) needs a real kernel and
root, so it is exercised by running `tmon` on a live host rather than unit-tested.
CI (`.github/workflows/build-tmon.yml`) builds everything and runs the suite in a
`debian:trixie` container on every change under `tmon-linux/`. Disable the tests
in a build with `-DTMON_BUILD_TESTS=OFF`.

### Dependency strategy

`libbpf` is statically linked (a bare Debian host is unlikely to have it).
`glibc` stays dynamic (present everywhere); `libelf`/`libz` are dynamic too —
static `libelf.a` on Debian drags in unpackaged elfutils-internal symbols, and
both shared libs are either universal (zlib) or a one-package install
(`libelf1`). `libstdc++`/`libgcc` are statically bound; CLI11 and cJSON are
compiled in. The result is a ~3 MB binary whose only runtime needs are glibc,
`libelf1`, `zlib1g`, and `libzstd1`.

## Running

`tmon` loads BPF programs and so needs `CAP_BPF`+`CAP_PERFMON` (or root):

```sh
sudo ./build/tmon -- /bin/echo hello
sudo ./build/tmon --format json -o run.jsonl -- ./my-primitive
```

## Status

v0.1: CMake scaffold, three-layer structure, from-birth tree-scoped syscall
capture with name resolution, human + JSONL output, `-o`, static-linked per the
strategy above. Argument decoding (`--decode`) and syscall-family excludes are
planned follow-ups.
