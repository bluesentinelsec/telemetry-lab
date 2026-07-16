using Tmon.Cli;
using Tmon.Model;
using Xunit;

namespace Tmon.Tests;

public class CommandLineTests
{
    private static ParseOutcome Parse(params string[] args) =>
        CommandLine.Parse(args, new StringWriter(), new StringWriter());

    [Fact]
    public void ExplicitCommandParsesWithDefaults()
    {
        var o = Parse("--", "app.exe", "arg1");
        Assert.True(o.ShouldRun);
        Assert.Equal(new[] { "app.exe", "arg1" }, o.Config!.Command);
        Assert.Equal(OutputFormat.Human, o.Config.Format);
        Assert.True(o.Config.Decode);
        Assert.True(o.Config.Follow);
    }

    [Fact]
    public void BareCommandFormWorks()
    {
        var o = Parse("app.exe", "arg1");
        Assert.True(o.ShouldRun);
        Assert.Equal(new[] { "app.exe", "arg1" }, o.Config!.Command);
    }

    [Fact]
    public void OptionsBeforeCommandAreParsed()
    {
        var o = Parse("-f", "json", "-o", "out.jsonl", "--no-follow", "-c", "-q",
                      "--no-decode", "-n", "5", "--buffer-mb", "128",
                      "--meta", "lang=c", "--", "app.exe");
        var c = o.Config!;
        Assert.Equal(OutputFormat.Json, c.Format);
        Assert.Equal("out.jsonl", c.OutputFile);
        Assert.False(c.Follow);
        Assert.True(c.SummaryOnly);
        Assert.True(c.Quiet);
        Assert.False(c.Decode);
        Assert.Equal(5UL, c.MaxEvents);
        Assert.Equal(128U, c.BufferMb);
        Assert.Equal("c", c.Meta["lang"]);
    }

    [Fact]
    public void InlineValueFormIsAccepted()
    {
        var o = Parse("--format=json", "--meta=run=demo", "app.exe");
        Assert.Equal(OutputFormat.Json, o.Config!.Format);
        Assert.Equal("demo", o.Config.Meta["run"]);
    }

    [Fact]
    public void CommandFlagsAreNotConsumedByTmon()
    {
        // Everything from the first positional on belongs to the command, even
        // tokens that look like tmon options.
        var o = Parse("-f", "json", "app.exe", "--format", "-c");
        Assert.Equal(new[] { "app.exe", "--format", "-c" }, o.Config!.Command);
        Assert.Equal(OutputFormat.Json, o.Config.Format);
    }

    [Fact]
    public void DoubleDashPassesEverythingThrough()
    {
        var o = Parse("--", "app.exe", "--format", "json");
        Assert.Equal(new[] { "app.exe", "--format", "json" }, o.Config!.Command);
    }

    [Fact]
    public void HelpAndVersionExitZeroWithoutRunning()
    {
        Assert.False(Parse("--help").ShouldRun);
        Assert.Equal(0, Parse("--help").ExitCode);
        Assert.Equal(0, Parse("--version").ExitCode);
    }

    public static IEnumerable<object[]> UsageErrorCases => new[]
    {
        new object[] { new string[0] },                          // no command
        new object[] { new[] { "--bogus", "--", "app" } },       // unknown option
        new object[] { new[] { "-f" } },                          // missing value
        new object[] { new[] { "-f", "xml", "--", "app" } },     // bad format
        new object[] { new[] { "--meta", "noeq", "--", "app" } },// bad meta
    };

    [Theory]
    [MemberData(nameof(UsageErrorCases))]
    public void UsageErrorsExitTwo(string[] args)
    {
        var o = Parse(args);
        Assert.False(o.ShouldRun);
        Assert.Equal(2, o.ExitCode);
    }

    [Fact]
    public void HelpTextGoesToStdoutNotStderr()
    {
        var stdout = new StringWriter();
        var stderr = new StringWriter();
        CommandLine.Parse(new[] { "--help" }, stdout, stderr);
        Assert.Contains("Usage: tmon", stdout.ToString());
        Assert.Equal("", stderr.ToString());
    }
}
