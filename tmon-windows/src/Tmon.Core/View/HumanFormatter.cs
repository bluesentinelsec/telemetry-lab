using System.Globalization;
using Tmon.Core;
using Tmon.Model;

namespace Tmon.View;

/// <summary>
/// Layer 3 — presentation. Renders the event stream in a human-readable,
/// strace-like form to a <see cref="TextWriter"/>. Implements
/// <see cref="IEventSink"/> so the engine drives it without knowing the format.
/// </summary>
public sealed class HumanFormatter : IEventSink
{
    private readonly TextWriter _out;
    private readonly Config _config;
    private double _firstMsec;
    private bool _haveFirst;
    // pid -> short image name, learned from process-start events, used as the
    // per-event "who" column (the Windows analog of Linux comm).
    private readonly Dictionary<int, string> _pidImage = new();

    public HumanFormatter(TextWriter output, Config config)
    {
        _out = output;
        _config = config;
    }

    public void Begin()
    {
        if (_config.SummaryOnly) return;
        _out.WriteLine($"tmon: tracing '{_config.Command[0]}'");
    }

    public void Handle(Event e)
    {
        if (e.Kind == EventKind.ProcessStart && e.Image is not null)
            _pidImage[e.Pid] = ShortName(e.Image);

        if (_config.SummaryOnly) return;

        double rel = RelativeSeconds(e.TimeMsec);
        _pidImage.TryGetValue(e.Pid, out var who);
        string prefix = string.Format(CultureInfo.InvariantCulture,
            "{0,11:F6} {1,-6} {2,-16} ", rel, e.Pid, who ?? "");
        _out.Write(prefix);

        switch (e.Kind)
        {
            case EventKind.Syscall:
                _out.Write(e.Syscall ?? "syscall");
                _out.WriteLine($"(@0x{e.SyscallAddress:x})");
                break;
            case EventKind.ProcessStart:
                _out.WriteLine($"+++ process start (ppid {e.ParentPid}){Quoted(e.Image)} +++");
                break;
            case EventKind.ProcessStop:
                _out.WriteLine($"+++ process stop (exit {e.ExitCode}) +++");
                break;
            case EventKind.Image:
                _out.WriteLine($"image{Quoted(e.Image)}");
                break;
        }
    }

    public void End(Summary s)
    {
        if (_config.Quiet) return;
        _out.WriteLine(
            $"tmon: {s.SyscallEvents} syscalls, {s.TotalEvents} events, " +
            $"{s.Processes} process(es), {s.Lost} lost; target exit {s.TargetExitCode}");
    }

    private double RelativeSeconds(double msec)
    {
        if (!_haveFirst || msec < _firstMsec)
        {
            _firstMsec = msec;
            _haveFirst = true;
        }
        return (msec - _firstMsec) / 1000.0;
    }

    private static string Quoted(string? s) => string.IsNullOrEmpty(s) ? "" : $" \"{s}\"";

    private static string ShortName(string path)
    {
        int slash = path.LastIndexOfAny(new[] { '\\', '/' });
        return slash >= 0 ? path[(slash + 1)..] : path;
    }
}
