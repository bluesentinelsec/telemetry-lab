using Tmon.Core;
using Tmon.Model;
using Tmon.View;

namespace Tmon.Cli;

/// <summary>
/// tmon (Windows) CLI. Parses argv into a Config (layer 1), selects a formatter
/// (layer 3), and runs the ETW capture engine (layer 2). The only place the
/// layers are wired together. The option surface matches tmon-linux; see --help.
/// </summary>
internal static class Program
{
    private const string Version = "tmon 0.1.0";

    private static int Main(string[] args)
    {
        var format = "human";
        string? output = null;
        bool noDecode = false, noReturns = false, noFollow = false, summary = false, quiet = false;
        ulong maxEvents = 0;
        uint bufferMb = 0;
        var meta = new Dictionary<string, string>();
        var command = new List<string>();

        // Split tmon's own options from the target command line using
        // prefix-command semantics: the command starts at the first positional
        // token, or after a literal "--".
        int i = 0;
        for (; i < args.Length; i++)
        {
            string a = args[i];
            if (a == "--") { i++; break; }
            if (a.Length == 0 || a[0] != '-') break; // first positional -> command

            string name = a;
            string? inlineVal = null;
            int eq = a.IndexOf('=');
            if (eq >= 0) { name = a[..eq]; inlineVal = a[(eq + 1)..]; }

            switch (name)
            {
                case "-h": case "--help": PrintHelp(Console.Out); return 0;
                case "--version": Console.Out.WriteLine(Version); return 0;
                case "-f": case "--format": format = inlineVal ?? Next(args, ref i, name); break;
                case "-o": case "--output": output = inlineVal ?? Next(args, ref i, name); break;
                case "--no-decode": noDecode = true; break;
                case "--no-returns": noReturns = true; break;
                case "--no-follow": noFollow = true; break;
                case "-c": case "--summary": summary = true; break;
                case "-q": case "--quiet": quiet = true; break;
                case "-n": case "--max-events":
                    if (!ulong.TryParse(inlineVal ?? Next(args, ref i, name), out maxEvents))
                        return Fail($"--max-events expects a number");
                    break;
                case "--buffer-mb":
                    if (!uint.TryParse(inlineVal ?? Next(args, ref i, name), out bufferMb))
                        return Fail($"--buffer-mb expects a number");
                    break;
                case "--meta":
                    {
                        string kv = inlineVal ?? Next(args, ref i, name);
                        int mEq = kv.IndexOf('=');
                        if (mEq <= 0) return Fail($"--meta expects KEY=VALUE, got '{kv}'");
                        meta[kv[..mEq]] = kv[(mEq + 1)..];
                        break;
                    }
                default:
                    return Fail($"unknown option '{a}'");
            }
        }
        for (; i < args.Length; i++) command.Add(args[i]);

        if (command.Count == 0)
        {
            Console.Error.WriteLine("tmon: no command given\n");
            PrintHelp(Console.Error);
            return 2;
        }
        if (format is not ("human" or "json"))
            return Fail($"--format must be 'human' or 'json', got '{format}'");

        var config = new Config
        {
            Command = command,
            Format = format == "json" ? OutputFormat.Json : OutputFormat.Human,
            OutputFile = output,
            Decode = !noDecode,
            CaptureReturns = !noReturns,
            Follow = !noFollow,
            SummaryOnly = summary,
            Quiet = quiet,
            MaxEvents = maxEvents,
            BufferMb = bufferMb,
            Meta = meta,
        };

        TextWriter? file = null;
        try
        {
            TextWriter outWriter = Console.Out;
            if (config.OutputFile is not null)
            {
                file = new StreamWriter(config.OutputFile, append: false);
                outWriter = file;
            }

            IEventSink sink = config.Format == OutputFormat.Json
                ? new JsonFormatter(outWriter, config)
                : new HumanFormatter(outWriter, config);

            int rc = new EtwEngine(config).Run(sink);
            return rc < 0 ? 1 : rc;
        }
        catch (IOException ex)
        {
            return Fail(ex.Message);
        }
        finally
        {
            file?.Flush();
            file?.Dispose();
        }
    }

    private static string Next(string[] args, ref int i, string name)
    {
        if (i + 1 >= args.Length)
        {
            Console.Error.WriteLine($"tmon: option '{name}' expects a value");
            Environment.Exit(2);
        }
        return args[++i];
    }

    private static int Fail(string message)
    {
        Console.Error.WriteLine($"tmon: {message}");
        return 2;
    }

    private static void PrintHelp(TextWriter w)
    {
        w.WriteLine("tmon — process-scoped telemetry monitor (ETW)");
        w.WriteLine();
        w.WriteLine("Usage: tmon [options] [--] <command> [args...]");
        w.WriteLine();
        w.WriteLine("Options:");
        w.WriteLine("  -h, --help                Show this help and exit");
        w.WriteLine("  --version                 Show version and exit");
        w.WriteLine("  -f, --format human|json   Output format (default human; json is JSONL)");
        w.WriteLine("  -o, --output FILE         Write output to FILE instead of stdout");
        w.WriteLine("  --no-decode               Do not decode event fields (paths); on by default");
        w.WriteLine("  --no-returns              No-op on Windows (ETW syscalls carry no return value)");
        w.WriteLine("  --no-follow               Do not follow process-tree descendants");
        w.WriteLine("  -c, --summary             Suppress the per-event stream; print only the summary");
        w.WriteLine("  -q, --quiet               Suppress the trailing summary line");
        w.WriteLine("  -n, --max-events N        Stop after N syscall events (0 = unlimited)");
        w.WriteLine("  --buffer-mb N             ETW session buffer size in MiB");
        w.WriteLine("  --meta KEY=VALUE          Attach metadata to machine-readable output (repeatable)");
    }
}
