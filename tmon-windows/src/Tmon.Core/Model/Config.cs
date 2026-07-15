namespace Tmon.Model;

/// <summary>Presentation format for the event stream.</summary>
public enum OutputFormat
{
    Human,
    Json,
}

/// <summary>
/// Layer 1 — data model. The fully-resolved run configuration: what to run, what
/// to capture, and how/where to emit it. The CLI builds one of these; the engine
/// consumes it. Nothing here parses argv. Mirrors the Linux tmon Config so the
/// two tools stay one consistent surface.
/// </summary>
public sealed class Config
{
    /// <summary>Target program and its arguments (index 0 is the program). Required.</summary>
    public required IReadOnlyList<string> Command { get; init; }

    public OutputFormat Format { get; init; } = OutputFormat.Human;

    /// <summary>Output destination; null means stdout.</summary>
    public string? OutputFile { get; init; }

    /// <summary>Decode event fields (image/file paths, network addresses). On by default.</summary>
    public bool Decode { get; init; } = true;

    /// <summary>
    /// Accepted for parity with Linux. Platform delta: ETW syscall events carry no
    /// per-call return value, so this is currently a no-op on Windows.
    /// </summary>
    public bool CaptureReturns { get; init; } = true;

    /// <summary>Follow process-tree descendants of the target. On by default.</summary>
    public bool Follow { get; init; } = true;

    /// <summary>Suppress the per-event stream; emit only the summary.</summary>
    public bool SummaryOnly { get; init; }

    /// <summary>Suppress the trailing summary line.</summary>
    public bool Quiet { get; init; }

    /// <summary>Stop after this many syscall events (0 = unlimited).</summary>
    public ulong MaxEvents { get; init; }

    /// <summary>ETW session buffer size in MiB (0 = library default).</summary>
    public uint BufferMb { get; init; }

    /// <summary>Free-form metadata stamped onto machine-readable output.</summary>
    public IReadOnlyDictionary<string, string> Meta { get; init; } =
        new Dictionary<string, string>();
}
