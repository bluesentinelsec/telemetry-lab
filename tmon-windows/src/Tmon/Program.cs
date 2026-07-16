using Tmon.Cli;
using Tmon.Core;
using Tmon.Model;
using Tmon.View;

namespace Tmon.App;

/// <summary>
/// tmon (Windows) entry point. Parses argv (layer: <see cref="CommandLine"/>),
/// selects a formatter (layer 3), and runs the ETW engine (layer 2). The only
/// place the layers are wired together.
/// </summary>
internal static class Program
{
    private static int Main(string[] args)
    {
        var outcome = CommandLine.Parse(args, Console.Out, Console.Error);
        if (!outcome.ShouldRun) return outcome.ExitCode;
        var config = outcome.Config!;

        TextWriter? file = null;
        try
        {
            TextWriter writer = Console.Out;
            if (config.OutputFile is not null)
            {
                file = new StreamWriter(config.OutputFile, append: false);
                writer = file;
            }

            IEventSink sink = config.Format == OutputFormat.Json
                ? new JsonFormatter(writer, config)
                : new HumanFormatter(writer, config);

            int rc = new EtwEngine(config).Run(sink);
            return rc < 0 ? 1 : rc;
        }
        catch (IOException ex)
        {
            Console.Error.WriteLine($"tmon: {ex.Message}");
            return 1;
        }
        finally
        {
            file?.Flush();
            file?.Dispose();
        }
    }
}
