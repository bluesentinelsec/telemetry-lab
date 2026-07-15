# PoC: Windows process-scoped telemetry monitor (C# / ETW / TraceEvent)

**Experimental — not for merge.** Windows counterpart to the Linux libbpf PoC:
proves we can run a specified subprocess and capture telemetry from *only* that
process and its descendants, excluding everything else.

## What it proves

Run on the lab's Windows Server 2025 host (as SYSTEM, via SSM):

```
> monitor cmd /c whoami
[monitor] tracing target pid=5488: cmd /c whoami
IMAGE      pid=5488  C:\Windows\System32\cmd.exe        # target, from birth
IMAGE      pid=5488  C:\Windows\System32\ntdll.dll
...
PROC-START pid=4292  ppid=5488  whoami.exe             # descendant added
IMAGE      pid=4292  C:\Windows\System32\whoami.exe
IMAGE      pid=4292  ...                                # descendant image loads
PROC-STOP  pid=4292  whoami.exe
PROC-STOP  pid=5488  cmd.exe
# only pids {5488, 4292} appear -- zero unrelated processes
```

- **From-birth capture** — `CREATE_SUSPENDED` gives us the PID before the target
  runs; we seed it, then `ResumeThread`. cmd.exe's own image load is captured.
- **Descendant scoping** — `whoami` (child of cmd) is added via the ETW
  `ProcessStart` event and fully traced.
- **Exclusion** — only the target tree's events are recorded.

## Design: spawn-and-trace (mirrors the Linux PoC)

The one structural difference from Linux: the Windows kernel ETW session is
**system-wide** — you cannot filter it to a PID in the kernel the way a BPF
program does. So scoping is enforced **in the consumer**: every event carries a
`ProcessID`, and we record only those in a traced-PID set. The set is seeded with
the `CREATE_SUSPENDED` target and grown to descendants via `ProcessStart`. Net
result is the same: only the target process tree is observed.

## Build & run

Dependencies: **.NET SDK** (install via `dotnet-install.ps1 -Channel 8.0`; not
present on the base AMI), the **`Microsoft.Diagnostics.Tracing.TraceEvent`**
NuGet package, and Administrator/SYSTEM (kernel ETW sessions require elevation).

```
dotnet build monitor.csproj -c Release
# runtime resolution: launch the DLL via the dotnet host, OR publish
# self-contained so the .exe needs no installed .NET on the lab host:
dotnet publish monitor.csproj -c Release -r win-x64 --self-contained
```

## Scope / caveats (for the production design)

- Captures process lifecycle + image (DLL) loads. Other families (file, network)
  attach the same way via the kernel provider keywords.
- **Syscall-level** events on Windows are the deeper follow-up: they need a
  suitable provider (syscall/PerfInfo or Threat-Intelligence) and thread->process
  attribution; not covered here.
- Consumer-side PID filtering means the session sees all events and drops
  non-tree ones; fine here, but high-volume families may need buffering care.
