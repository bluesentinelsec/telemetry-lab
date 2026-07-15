using Tmon.Core;
using Xunit;

namespace Tmon.Tests;

public class CommandLineBuildTests
{
    [Fact]
    public void PlainArgsJoinWithSpaces()
    {
        Assert.Equal("app.exe /c echo hi",
            EtwEngine.BuildCommandLine(new[] { "app.exe", "/c", "echo", "hi" }));
    }

    [Fact]
    public void ArgsWithSpacesAreQuoted()
    {
        Assert.Equal("app.exe \"c:\\Program Files\\x\"",
            EtwEngine.BuildCommandLine(new[] { "app.exe", @"c:\Program Files\x" }));
    }

    [Fact]
    public void EmbeddedQuotesAreEscaped()
    {
        Assert.Equal("app.exe \"a\\\"b\"",
            EtwEngine.BuildCommandLine(new[] { "app.exe", "a\"b" }));
    }
}
