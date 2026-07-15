using System.Text.Json;
using Tmon.Core;
using Tmon.Model;
using Tmon.View;
using Xunit;

namespace Tmon.Tests;

public class FormatterTests
{
    private static Config Basic(OutputFormat fmt = OutputFormat.Human, bool summaryOnly = false,
        bool quiet = false) => new()
    {
        Command = new[] { "app.exe" },
        Format = fmt,
        SummaryOnly = summaryOnly,
        Quiet = quiet,
        Meta = new Dictionary<string, string> { ["lang"] = "c" },
    };

    // --- Human ---------------------------------------------------------------

    [Fact]
    public void HumanRendersEachKind()
    {
        var sw = new StringWriter();
        var f = new HumanFormatter(sw, Basic());
        f.Handle(new Event { Kind = EventKind.ProcessStart, Pid = 10, ParentPid = 4, Image = @"C:\Windows\System32\cmd.exe" });
        f.Handle(new Event { Kind = EventKind.Image, Pid = 10, Image = @"C:\Windows\System32\ntdll.dll" });
        f.Handle(new Event { Kind = EventKind.Syscall, Pid = 10, Tid = 11, SyscallAddress = 0xdeadbeef });
        f.Handle(new Event { Kind = EventKind.ProcessStop, Pid = 10, ExitCode = 0 });

        var s = sw.ToString();
        Assert.Contains("process start (ppid 4) \"C:\\Windows\\System32\\cmd.exe\"", s);
        Assert.Contains("image \"C:\\Windows\\System32\\ntdll.dll\"", s);
        Assert.Contains("syscall(@0xdeadbeef)", s);
        Assert.Contains("process stop (exit 0)", s);
        // cmd.exe short name is used as the "who" column for the pid.
        Assert.Contains("cmd.exe", s);
    }

    [Fact]
    public void HumanUsesResolvedSyscallNameWhenPresent()
    {
        var sw = new StringWriter();
        var f = new HumanFormatter(sw, Basic());
        f.Handle(new Event { Kind = EventKind.Syscall, Pid = 10, Syscall = "NtCreateFile", SyscallAddress = 0x1000 });
        Assert.Contains("NtCreateFile", sw.ToString());
    }

    [Fact]
    public void SummaryOnlySuppressesEventsButEndPrintsTotals()
    {
        var sw = new StringWriter();
        var f = new HumanFormatter(sw, Basic(summaryOnly: true));
        f.Handle(new Event { Kind = EventKind.Syscall, Pid = 10 });
        Assert.Equal("", sw.ToString());
        f.End(new Summary { SyscallEvents = 5, TotalEvents = 7, Processes = 1 });
        Assert.Contains("5 syscalls", sw.ToString());
    }

    [Fact]
    public void QuietSuppressesSummary()
    {
        var sw = new StringWriter();
        var f = new HumanFormatter(sw, Basic(quiet: true));
        f.End(new Summary { SyscallEvents = 1 });
        Assert.Equal("", sw.ToString());
    }

    // --- JSON ----------------------------------------------------------------

    private static JsonElement ParseLine(string line) => JsonDocument.Parse(line).RootElement;

    [Fact]
    public void JsonMetaRecordCarriesCommandAndMeta()
    {
        var sw = new StringWriter();
        new JsonFormatter(sw, Basic(OutputFormat.Json)).Begin();
        var j = ParseLine(sw.ToString().Trim());
        Assert.Equal("meta", j.GetProperty("record").GetString());
        Assert.Equal("windows", j.GetProperty("os").GetString());
        Assert.Equal("app.exe", j.GetProperty("command")[0].GetString());
        Assert.Equal("c", j.GetProperty("meta").GetProperty("lang").GetString());
    }

    [Fact]
    public void JsonSyscallEventHasAddressAndIds()
    {
        var sw = new StringWriter();
        new JsonFormatter(sw, Basic(OutputFormat.Json))
            .Handle(new Event { Kind = EventKind.Syscall, Pid = 10, Tid = 11, SyscallAddress = 0xabc });
        var j = ParseLine(sw.ToString().Trim());
        Assert.Equal("event", j.GetProperty("record").GetString());
        Assert.Equal("syscall", j.GetProperty("kind").GetString());
        Assert.Equal(10, j.GetProperty("pid").GetInt32());
        Assert.Equal("0xabc", j.GetProperty("syscall_address").GetString());
    }

    [Fact]
    public void JsonProcessStartHasPpidAndImage()
    {
        var sw = new StringWriter();
        new JsonFormatter(sw, Basic(OutputFormat.Json))
            .Handle(new Event { Kind = EventKind.ProcessStart, Pid = 10, ParentPid = 4, Image = "cmd.exe" });
        var j = ParseLine(sw.ToString().Trim());
        Assert.Equal("process_start", j.GetProperty("kind").GetString());
        Assert.Equal(4, j.GetProperty("ppid").GetInt32());
        Assert.Equal("cmd.exe", j.GetProperty("image").GetString());
    }

    [Fact]
    public void JsonSummaryReportsCounts()
    {
        var sw = new StringWriter();
        new JsonFormatter(sw, Basic(OutputFormat.Json))
            .End(new Summary { SyscallEvents = 3, TotalEvents = 4, Processes = 2, Lost = 0, TargetExitCode = 1 });
        var j = ParseLine(sw.ToString().Trim());
        Assert.Equal("summary", j.GetProperty("record").GetString());
        Assert.Equal(3, j.GetProperty("syscall_events").GetInt64());
        Assert.Equal(2, j.GetProperty("processes").GetInt32());
        Assert.Equal(1, j.GetProperty("target_exit_code").GetInt32());
    }
}
