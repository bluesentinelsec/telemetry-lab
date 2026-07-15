using System.Text.Json.Nodes;
using Tmon.Core;
using Tmon.Model;

namespace Tmon.View;

/// <summary>
/// Layer 3 — presentation. Renders the event stream as JSONL (one JSON object per
/// line) to a <see cref="TextWriter"/>. Every line carries a "record" field so a
/// consumer can tell meta/event/summary rows apart — the same schema shape as the
/// Linux tool, so downstream pipeline steps stay OS-agnostic.
/// </summary>
public sealed class JsonFormatter : IEventSink
{
    private readonly TextWriter _out;
    private readonly Config _config;

    public JsonFormatter(TextWriter output, Config config)
    {
        _out = output;
        _config = config;
    }

    public void Begin()
    {
        var root = new JsonObject
        {
            ["record"] = "meta",
            ["tool"] = "tmon",
            ["os"] = "windows",
            ["command"] = new JsonArray(_config.Command.Select(s => JsonValue.Create(s)).ToArray()),
        };
        if (_config.Meta.Count > 0)
        {
            var meta = new JsonObject();
            foreach (var kv in _config.Meta) meta[kv.Key] = kv.Value;
            root["meta"] = meta;
        }
        WriteLine(root);
    }

    public void Handle(Event e)
    {
        var root = new JsonObject
        {
            ["record"] = "event",
            ["kind"] = KindName(e.Kind),
            ["time_msec"] = e.TimeMsec,
            ["pid"] = e.Pid,
        };
        switch (e.Kind)
        {
            case EventKind.Syscall:
                root["tid"] = e.Tid;
                root["syscall_address"] = $"0x{e.SyscallAddress:x}";
                if (e.Syscall is not null) root["syscall"] = e.Syscall;
                break;
            case EventKind.ProcessStart:
                root["ppid"] = e.ParentPid;
                if (e.Image is not null) root["image"] = e.Image;
                break;
            case EventKind.ProcessStop:
                root["exit_code"] = e.ExitCode;
                if (e.Image is not null) root["image"] = e.Image;
                break;
            case EventKind.Image:
                if (e.Image is not null) root["image"] = e.Image;
                break;
        }
        WriteLine(root);
    }

    public void End(Summary s)
    {
        var root = new JsonObject
        {
            ["record"] = "summary",
            ["syscall_events"] = s.SyscallEvents,
            ["total_events"] = s.TotalEvents,
            ["processes"] = s.Processes,
            ["lost"] = s.Lost,
            ["target_exit_code"] = s.TargetExitCode,
        };
        WriteLine(root);
    }

    private void WriteLine(JsonObject obj) => _out.WriteLine(obj.ToJsonString());

    private static string KindName(EventKind kind) => kind switch
    {
        EventKind.Syscall => "syscall",
        EventKind.ProcessStart => "process_start",
        EventKind.ProcessStop => "process_stop",
        EventKind.Image => "image",
        _ => "unknown",
    };
}
