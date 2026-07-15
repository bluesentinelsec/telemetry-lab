# PoC: Linux process-scoped telemetry monitor (libbpf CO-RE)

**Experimental — not for merge.** Proves the core requirement for the Linux
telemetry monitor: run a specified subprocess and collect telemetry from *only*
that process and its descendants, excluding everything else on the host.

## What it proves

Run on the lab's Debian 13 host (kernel 6.12, BTF present):

```
[monitor] tracing target tgid=2896: ./spawner
SYS   pid=2896 tid=2896 comm=monitor  nr=59      # execve captured from birth
EXEC  pid=2896 comm=spawner
SYS   pid=2896 tid=2896 comm=spawner   nr=...     # target syscalls
FORK  pid=2896 -> child=2897 comm=spawner         # descendant added
EXEC  pid=2897 comm=id
SYS   pid=2897 tid=2897 comm=id        nr=...     # descendant syscalls
...
# unique comms observed: only {monitor, spawner, id} -- zero unrelated processes
```

- **From-birth capture:** the `execve` is recorded (syscall 59) before the
  target's `comm` even changes — nothing is missed before `main`.
- **Descendant scoping:** the forked child (`id`) is fully traced via the BPF
  `sched_process_fork` hook.
- **Exclusion:** on a busy host, only the target process tree appears.

## Design: spawn-and-trace

`monitor.c` forks the target and stops it (`SIGSTOP`) *before* it execs, arms the
BPF filter on the target's tgid, then releases it (`SIGCONT`). Owning the process
from birth is what makes both from-birth capture and precise tree-scoping
possible. `monitor.bpf.c` keeps a hash map of traced tgids: user space seeds it
with the target; the fork hook adds descendants; the exit hook removes them; the
`raw_syscalls:sys_enter` tracepoint records syscalls only for members.

## Build & run

Dependencies: `clang`, `libbpf-dev`, `bpftool`, `linux-headers-$(uname -r)`,
`libelf-dev`, `zlib1g-dev`, `make`; a kernel with BTF (`/sys/kernel/btf/vmlinux`).

```sh
make
sudo ./monitor ./spawner       # or: sudo ./monitor <any command> [args...]
```

## Scope / caveats (for the production design)

- Syscalls only (via `raw_syscalls:sys_enter`); the real monitor adds the other
  telemetry families (file, network, library load, process/thread) as separate
  programs gated on the same traced-tgid map.
- Descendant tracking keys on tgid and treats `sched_process_fork`'s
  `parent_pid` as a tgid — correct for single-threaded subjects; the production
  version should resolve the thread-group leader for multi-threaded processes.
- No syscall-argument decoding or name resolution yet (numbers only).
