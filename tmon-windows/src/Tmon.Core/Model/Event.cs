namespace Tmon.Model;

/// <summary>The kind of action a record describes.</summary>
public enum EventKind
{
    Syscall,
    ProcessStart,
    ProcessStop,
    Image,
    File,
    Network,
    Registry,
}

/// <summary>
/// Layer 1 — data model. One observed action from a traced process (or its
/// descendants). A plain value type with no behavior. The engine produces these;
/// formatters consume them. Kind-specific fields are null/zero when not relevant.
/// </summary>
public sealed class Event
{
    public EventKind Kind { get; init; }

    /// <summary>Milliseconds since the trace session started (monotonic).</summary>
    public double TimeMsec { get; init; }

    public int Pid { get; init; }
    public int Tid { get; init; }

    // --- Syscall ---
    public ulong SyscallAddress { get; init; }
    /// <summary>Resolved syscall routine name, if symbol resolution is available.</summary>
    public string? Syscall { get; init; }

    // --- ProcessStart / ProcessStop ---
    public int ParentPid { get; init; }
    public int ExitCode { get; init; }

    // --- ProcessStart / Image ---
    /// <summary>Image/library path (process image on start; module path on image load).</summary>
    public string? Image { get; init; }

    // --- File / Network ---
    /// <summary>Sub-operation: file (create/read/write/delete/rename) or net (connect/send/recv/...).</summary>
    public string? Operation { get; init; }

    // --- File ---
    public string? Path { get; init; }
    public long Size { get; init; }    // File read/write, or Network send/recv byte count
    public long Offset { get; init; }  // File read/write offset

    // --- Network ---
    public string? Protocol { get; init; }  // "tcp" or "udp"
    public string? Local { get; init; }     // local "ip:port"
    public string? Remote { get; init; }    // remote "ip:port"

    // --- Registry ---
    // Path holds the key; ValueName holds the value (for query/set/delete_value).
    public string? ValueName { get; init; }
}
