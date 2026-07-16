using Tmon.Model;

namespace Tmon.Core;

/// <summary>End-of-run totals, handed to the sink once capture finishes.</summary>
public sealed class Summary
{
    public long TotalEvents { get; set; }
    public long SyscallEvents { get; set; }
    public int Processes { get; set; }        // distinct pids observed
    public long Lost { get; set; }            // events lost to ETW buffer pressure
    public int TargetExitCode { get; set; }
}

/// <summary>
/// Layer 2 boundary between capture and presentation. The engine drives an
/// <see cref="IEventSink"/>; concrete sinks (the formatters) decide how a run
/// becomes bytes. The engine depends only on this abstraction.
/// </summary>
public interface IEventSink
{
    /// <summary>Called once before any events, so a sink can emit a preamble.</summary>
    void Begin();

    /// <summary>Called for every captured event.</summary>
    void Handle(Event e);

    /// <summary>Called once after the last event with run totals.</summary>
    void End(Summary summary);
}
