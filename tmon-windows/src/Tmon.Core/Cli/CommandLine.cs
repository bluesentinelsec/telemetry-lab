using Tmon.Model;

namespace Tmon.Cli;

/// <summary>
/// Result of parsing argv: either a ready <see cref="Config"/> to run, or an exit
/// code (help/version printed = 0, usage error = 2) with nothing to run.
/// </summary>
public sealed class ParseOutcome
{
    public Config? Config { get; private init; }
    public int ExitCode { get; private init; }

    /// <summary>True when a Config is ready and the engine should run.</summary>
    public bool ShouldRun => Config is not null;

    public static ParseOutcome Ready(Config config) => new() { Config = config };
    public static ParseOutcome Exit(int code) => new() { ExitCode = code };
}

/// <summary>
/// tmon's argument parser. Kept out of Program.cs so it is unit-testable without
/// spawning a process. Uses prefix-command semantics identical to tmon-linux: the
/// target command starts at the first positional token, or after a literal "--".
/// </summary>
public static class CommandLine
{
    public const string Version = "tmon 0.1.0";

    public static ParseOutcome Parse(string[] args, TextWriter stdout, TextWriter stderr)
    {
        var format = "human";
        string? output = null;
        bool noDecode = false, noReturns = false, noFollow = false, summary = false, quiet = false;
        ulong maxEvents = 0;
        uint bufferMb = 0;
        var meta = new Dictionary<string, string>();
        var command = new List<string>();

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
                case "-h": case "--help": PrintHelp(stdout); return ParseOutcome.Exit(0);
                case "--version": stdout.WriteLine(Version); return ParseOutcome.Exit(0);
                case "-f": case "--format":
                    if (!TryValue(args, ref i, name, inlineVal, stderr, out format)) return ParseOutcome.Exit(2);
                    break;
                case "-o": case "--output":
                    if (!TryValue(args, ref i, name, inlineVal, stderr, out output)) return ParseOutcome.Exit(2);
                    break;
                case "--no-decode": noDecode = true; break;
                case "--no-returns": noReturns = true; break;
                case "--no-follow": noFollow = true; break;
                case "-c": case "--summary": summary = true; break;
                case "-q": case "--quiet": quiet = true; break;
                case "-n": case "--max-events":
                    if (!TryValue(args, ref i, name, inlineVal, stderr, out var mv)) return ParseOutcome.Exit(2);
                    if (!ulong.TryParse(mv, out maxEvents)) return Fail(stderr, "--max-events expects a number");
                    break;
                case "--buffer-mb":
                    if (!TryValue(args, ref i, name, inlineVal, stderr, out var bv)) return ParseOutcome.Exit(2);
                    if (!uint.TryParse(bv, out bufferMb)) return Fail(stderr, "--buffer-mb expects a number");
                    break;
                case "--meta":
                    if (!TryValue(args, ref i, name, inlineVal, stderr, out var kv)) return ParseOutcome.Exit(2);
                    int mEq = kv.IndexOf('=');
                    if (mEq <= 0) return Fail(stderr, $"--meta expects KEY=VALUE, got '{kv}'");
                    meta[kv[..mEq]] = kv[(mEq + 1)..];
                    break;
                default:
                    return Fail(stderr, $"unknown option '{a}'");
            }
        }
        for (; i < args.Length; i++) command.Add(args[i]);

        if (command.Count == 0)
        {
            stderr.WriteLine("tmon: no command given\n");
            PrintHelp(stderr);
            return ParseOutcome.Exit(2);
        }
        if (format is not ("human" or "json"))
            return Fail(stderr, $"--format must be 'human' or 'json', got '{format}'");

        return ParseOutcome.Ready(new Config
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
        });
    }

    private static bool TryValue(string[] args, ref int i, string name, string? inlineVal,
        TextWriter stderr, out string value)
    {
        if (inlineVal is not null) { value = inlineVal; return true; }
        if (i + 1 >= args.Length)
        {
            stderr.WriteLine($"tmon: option '{name}' expects a value");
            value = "";
            return false;
        }
        value = args[++i];
        return true;
    }

    private static ParseOutcome Fail(TextWriter stderr, string message)
    {
        stderr.WriteLine($"tmon: {message}");
        return ParseOutcome.Exit(2);
    }

    public static void PrintHelp(TextWriter w)
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
