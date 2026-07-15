# tmon-windows

`tmon` (telemetry monitor) for Windows — the ETW counterpart to
[`tmon-linux`](../tmon-linux). It spawns a target program, follows its process
tree, and records telemetry from **only that tree**, with the **same CLI** as the
Linux tool except where the platform genuinely differs. Written in C# / .NET 8.

Like the Linux tool, it uses a spawn-and-trace model: create the target
suspended so we own its PID before it runs, start a real-time NT Kernel ETW
session, seed the traced set with the target, then resume it — growing the set to
descendants via process-start events. Because the kernel session is system-wide,
scoping is enforced consumer-side (unlike Linux's in-kernel BPF filter). Syscalls
are attributed by chaining CPU → running thread (context switches) → process
(thread events) → the traced set.

## Source layout (three layers, mirroring tmon-linux)

| Layer | Path | Responsibility |
|---|---|---|
| 1 — data model | `src/Tmon.Core/Model/` | `Event`, `Config` value types |
| 2 — business logic | `src/Tmon.Core/Core/` | `EtwEngine` (capture), `IEventSink`, `Summary` |
| 3 — presentation | `src/Tmon.Core/View/` | `HumanFormatter`, `JsonFormatter` |
| CLI | `src/Tmon/Program.cs` | Arg parsing; the only place the layers are wired |

## CLI

`tmon [options] [--] <command> [args...]` — same surface as tmon-linux (`-f/--format`,
`-o/--output`, `--no-follow`, `-c/--summary`, `-q/--quiet`, `-n/--max-events`,
`--buffer-mb`, `--meta`, `--no-decode`). Run `tmon --help` for the full list.

Platform deltas: `--buffer-mb` sizes the **ETW session buffer** (Linux: the BPF
ring); `--no-returns` is accepted but a **no-op** (ETW syscall events carry no
per-call return value); syscalls are reported by handler **address** (name
resolution is a later increment), and richer named events (`process_start`,
`process_stop`, `image`, later `file`/`network`) are the Windows decoded signal.

## Building

Requires the .NET 8 SDK and Windows (ETW is Windows-only).

```pwsh
dotnet build src/Tmon/Tmon.csproj -c Release
# Self-contained exe for lab hosts (no .NET runtime needed on the target):
dotnet publish src/Tmon/Tmon.csproj -c Release -r win-x64 --self-contained
```

## Running

Opening an NT Kernel ETW session requires elevation:

```pwsh
# Administrator / SYSTEM (SSM RunCommand runs as SYSTEM):
tmon -- .\primitive.exe
tmon --format json -o run.jsonl -- .\primitive.exe
```

## Status

v0.1: three-layer scaffold, CLI at parity with tmon-linux, spawn-and-trace,
tree-scoped process/thread/image capture and syscall attribution, human + JSONL
output, lost-event accounting. Planned: syscall name resolution via kernel
symbols, `FileIO`/`TcpIp` decoding (paths, addresses), unit tests + CI.
