# ttp-composite

Behavioral **composite** techniques for the telemetry-lab study's tier-2
question: *does execution substrate change whether a shipped behavioral
detection fires?* Where `ttp-primitives` measures raw telemetry **emission**,
`ttp-composite` measures **detection outcomes** — each composite is an ATT&CK
technique implemented natively across the substrate matrix and detonated against
an unmodified, shipped detector (Falco on Linux).

Composites are validated by **whether a rule fires**, not by unit tests, so
(unlike the primitives) they carry no test harness.

## Layout

```
ttp-composite/linux/{c,cpp,go,rust}/<composite>/   # one native impl per substrate language
ttp-composite/linux/detonate/fire-matrix.sh        # the detonation harness (runs on the lab host)
```

Linux composites detonate **in a container** (Falco's representative deployment),
because the mover's rule is container-gated. The container is a single constant
base image (`lab-substrate:13`) held fixed across the whole matrix, so it is a
constant offset rather than a per-substrate variable (see lab issue #39).

## Composites (Linux)

| Composite | ATT&CK | Falco rule (unmodified, shipped) | Role |
|---|---|---|---|
| `reverse_shell` | T1059 | Redirect STDOUT/STDIN to Network Connection in Container | **mover** (mechanism-keyed) |
| `imds` | T1552.005 | Contact EC2 Instance Metadata Service From Container | connect-seam probe |
| `read_sensitive_file` | T1555 | Read sensitive file untrusted | robustness control |
| `symlink_sensitive` | T1555 | Create Symlink Over Sensitive Files | robustness control |
| `clear_log` | T1070 | Clear Log Activities | robustness control |
| `mkdir_bin` | T1222.002 | Mkdir binary dirs | robustness control |
| `ptrace_antidebug` | T1622 | PTRACE anti-debug attempt | robustness control |

Rules come from Falco's **default + incubating + sandbox** rulesets, unmodified.
(`imds` needs the incubating set and `mkdir_bin` the sandbox set — the lab loads
all three; see `lab-environment`.)

## Result (fire matrix, 7 composites × 8 Linux substrates)

Measured on the live lab (Debian 13, Falco modern-eBPF, in-container detonation):

```
composite             c-glibc c-musl cpp-stdc++ cpp-libc++ go-cgo go-static rust-gnu rust-musl
reverse_shell            F      F        F          F        .       .         F        F
imds                     F      F        F          F        F       F         F        F
read_sensitive_file      F      F        F          F        F       F         F        F
symlink_sensitive        F      F        F          F        F       F         F        F
clear_log                F      F        F          F        F       F         F        F
mkdir_bin                F      F        F          F        F       F         F        F
ptrace_antidebug         F      F        F          F        F       F         F        F
```

**One substrate-fragile rule** (`reverse_shell`, which both Go builds evade) among
six robust ones. Fragility is concentrated in the single **mechanism-keyed**
predicate (`fd.type in (ipv4,ipv6)` on duplicated stdio); every **effect-keyed**
rule is robust across all eight substrates. This is the decoupling + boundary
result: emission varies enormously across substrates (see `ttp-primitives`), yet
shipped behavioral detections almost never flip — except where a rule keys on a
substrate-variable *mechanism* rather than the substrate-invariant *effect*.

## Why Go evades — the mechanism

The reverse shell is identical behavior with a different runtime I/O model,
captured under `tmon`:

| `reverse_shell` | socket | connect | dup2 | dup3 | pipe2 | shell stdio fd.type | rule |
|---|---|---|---|---|---|---|---|
| C / C++ / Rust | 2 | 1 | **3** | 0 | 0 | **ipv4** (socket → stdio) | fires |
| Go | 2 | 1 | 0 | **3** | **4** | **fifo** (pipe → stdio) | evades |

C/C++/Rust `dup2` the connected socket directly onto the shell's fd 0/1/2
(`fd.type=ipv4`). Go's `os/exec` cannot hand a `net.Conn` (not an `*os.File`) to
the child, so it creates OS pipes (`pipe2`) and `dup3`s those onto the shell's
stdio, relaying bytes with goroutines — the shell's stdio are FIFOs
(`fd.type=fifo`), so the rule never matches. The evasion is a property of the
**language runtime's process/IO model**, not of libc linkage.

## Reproduce

Build the composites for the 8 configs (mirrors the primitives' toolchains:
gcc/musl-gcc, clang++ libstdc++/libc++, CGO on/off, rustc gnu/musl), stage the
binaries on the Debian lab host under `/opt/lab/compdist/<config>/`, then run the
harness on the host:

```sh
bash ttp-composite/linux/detonate/fire-matrix.sh
```

It detonates each composite in the constant base image and reports, per
`substrate × composite`, which shipped Falco rule fired (filtering the bind-mount
injection noise). Capture each composite's own in-container telemetry with `tmon`
for the mechanism view.
