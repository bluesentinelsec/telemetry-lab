using System.Collections.Concurrent;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Diagnostics.Tracing.Parsers;
using Microsoft.Diagnostics.Tracing.Parsers.Kernel;
using Microsoft.Diagnostics.Tracing.Session;
using Tmon.Model;

namespace Tmon.Core;

/// <summary>
/// Layer 2 — business logic. The capture engine. Spawns the target suspended,
/// starts a real-time NT Kernel ETW session, scopes events to the target's
/// process tree (consumer-side, since the kernel session is system-wide), and
/// pumps them into an <see cref="IEventSink"/>. Returns the target's exit code.
///
/// Syscall attribution is the subtle part: PerfInfo SysCall events carry only a
/// ProcessorNumber, so we chain CPU -> running thread (from context switches) ->
/// process (from thread events) -> the traced set.
/// </summary>
public sealed class EtwEngine
{
    private readonly Config _config;

    // Cross-thread state: the main thread seeds these; the ETW consumer thread
    // reads/updates them.
    private readonly ConcurrentDictionary<int, byte> _traced = new();
    private readonly ConcurrentDictionary<int, int> _threadToPid = new();
    private readonly ConcurrentDictionary<int, int> _cpuToTid = new();
    private readonly HashSet<int> _pids = new();

    private IEventSink _sink = null!;
    private readonly Summary _summary = new();
    private int _targetPid;
    private bool _targetStartEmitted;
    private volatile bool _maxReached;

    public EtwEngine(Config config) => _config = config;

    public int Run(IEventSink sink)
    {
        _sink = sink;

        if (!(TraceEventSession.IsElevated() ?? false))
        {
            Console.Error.WriteLine("tmon: must run elevated (Administrator/SYSTEM) to open a kernel ETW session");
            return -1;
        }

        using var session = new TraceEventSession(KernelTraceEventParser.KernelSessionName);
        if (_config.BufferMb > 0)
            session.BufferSizeMB = (int)_config.BufferMb;

        session.EnableKernelProvider(
            KernelTraceEventParser.Keywords.Process |
            KernelTraceEventParser.Keywords.Thread |
            KernelTraceEventParser.Keywords.ImageLoad |
            KernelTraceEventParser.Keywords.ContextSwitch |
            KernelTraceEventParser.Keywords.SystemCall);

        WireHandlers(session.Source.Kernel);

        _sink.Begin();

        var consumer = new Thread(() =>
        {
            try { session.Source.Process(); }
            catch (Exception ex) { Console.Error.WriteLine($"tmon: ETW consumer stopped: {ex.Message}"); }
        }) { IsBackground = true, Name = "tmon-etw" };
        consumer.Start();
        Thread.Sleep(500); // let the session start consuming before we launch

        if (!Spawn(out var pi))
        {
            session.Stop();
            return -1;
        }

        // Run to completion, or until we hit --max-events (then terminate it).
        int exitCode = 0;
        while (true)
        {
            uint wait = WaitForSingleObject(pi.hProcess, 100);
            if (wait == WAIT_OBJECT_0)
            {
                GetExitCodeProcess(pi.hProcess, out exitCode);
                break;
            }
            if (_maxReached)
            {
                TerminateProcess(pi.hProcess, 1);
                WaitForSingleObject(pi.hProcess, 2000);
                exitCode = 1;
                break;
            }
        }

        Thread.Sleep(750);   // drain events buffered after the target exited
        session.Stop();
        consumer.Join(2000);

        _summary.TargetExitCode = exitCode;
        _summary.Processes = _pids.Count;
        _summary.Lost = session.Source.EventsLost;
        _sink.End(_summary);

        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);
        return exitCode;
    }

    private void WireHandlers(KernelTraceEventParser k)
    {
        // Thread -> process (DCStart covers threads that predate the session).
        k.ThreadStart += e => _threadToPid[e.ThreadID] = e.ProcessID;
        k.ThreadDCStart += e => _threadToPid[e.ThreadID] = e.ProcessID;

        // CPU -> currently scheduled thread, for syscall attribution.
        k.ThreadCSwitch += e => _cpuToTid[e.ProcessorNumber] = e.NewThreadID;

        k.PerfInfoSysClEnter += e =>
        {
            if (_cpuToTid.TryGetValue(e.ProcessorNumber, out var tid) &&
                _threadToPid.TryGetValue(tid, out var pid) &&
                _traced.ContainsKey(pid))
            {
                Emit(new Event
                {
                    Kind = EventKind.Syscall,
                    TimeMsec = e.TimeStampRelativeMSec,
                    Pid = pid,
                    Tid = tid,
                    SyscallAddress = e.SysCallAddress,
                });
            }
        };

        k.ProcessStart += e =>
        {
            bool isTarget = e.ProcessID == _targetPid;
            bool isChild = _traced.ContainsKey(e.ParentID);
            if (isTarget && !_targetStartEmitted)
            {
                _targetStartEmitted = true;
                EmitProcess(EventKind.ProcessStart, e);
            }
            else if (isChild && _config.Follow)
            {
                _traced[e.ProcessID] = 1;
                EmitProcess(EventKind.ProcessStart, e);
            }
        };

        k.ProcessStop += e =>
        {
            if (_traced.ContainsKey(e.ProcessID))
            {
                EmitProcess(EventKind.ProcessStop, e);
                _traced.TryRemove(e.ProcessID, out _);
            }
        };

        k.ImageLoad += e =>
        {
            if (_traced.ContainsKey(e.ProcessID))
                Emit(new Event
                {
                    Kind = EventKind.Image,
                    TimeMsec = e.TimeStampRelativeMSec,
                    Pid = e.ProcessID,
                    Image = _config.Decode ? e.FileName : null,
                });
        };
    }

    private void EmitProcess(EventKind kind, ProcessTraceData e) => Emit(new Event
    {
        Kind = kind,
        TimeMsec = e.TimeStampRelativeMSec,
        Pid = e.ProcessID,
        ParentPid = e.ParentID,
        ExitCode = kind == EventKind.ProcessStop ? e.ExitStatus : 0,
        Image = _config.Decode ? e.ImageFileName : null,
    });

    // Called only on the ETW consumer thread, so counters and the sink need no lock.
    private void Emit(Event e)
    {
        _summary.TotalEvents++;
        if (e.Kind == EventKind.Syscall)
        {
            _summary.SyscallEvents++;
            if (_config.MaxEvents != 0 && (ulong)_summary.SyscallEvents >= _config.MaxEvents)
                _maxReached = true;
        }
        _pids.Add(e.Pid);
        _sink.Handle(e);
    }

    private bool Spawn(out PROCESS_INFORMATION pi)
    {
        var si = new STARTUPINFO();
        si.cb = Marshal.SizeOf<STARTUPINFO>();
        string cmdline = BuildCommandLine(_config.Command);
        if (!CreateProcess(null!, new StringBuilder(cmdline), IntPtr.Zero, IntPtr.Zero, false,
                CREATE_SUSPENDED, IntPtr.Zero, null!, ref si, out pi))
        {
            Console.Error.WriteLine($"tmon: CreateProcess failed: {Marshal.GetLastWin32Error()}");
            return false;
        }

        _targetPid = pi.dwProcessId;
        _traced[_targetPid] = 1;
        _threadToPid[pi.dwThreadId] = pi.dwProcessId; // seed the main thread
        ResumeThread(pi.hThread);
        return true;
    }

    /// <summary>Quote args per Windows CreateProcess rules (simplified).</summary>
    internal static string BuildCommandLine(IReadOnlyList<string> args)
    {
        var sb = new StringBuilder();
        foreach (var a in args)
        {
            if (sb.Length > 0) sb.Append(' ');
            if (a.Length > 0 && !a.Contains(' ') && !a.Contains('"') && !a.Contains('\t'))
                sb.Append(a);
            else
                sb.Append('"').Append(a.Replace("\"", "\\\"")).Append('"');
        }
        return sb.ToString();
    }

    // --- Win32 interop ---
    private const uint CREATE_SUSPENDED = 0x4;
    private const uint WAIT_OBJECT_0 = 0x0;

    [StructLayout(LayoutKind.Sequential)]
    private struct STARTUPINFO
    {
        public int cb;
        public IntPtr lpReserved, lpDesktop, lpTitle;
        public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public ushort wShowWindow, cbReserved2;
        public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PROCESS_INFORMATION
    {
        public IntPtr hProcess, hThread;
        public int dwProcessId, dwThreadId;
    }

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CreateProcess(string lpApplicationName, StringBuilder lpCommandLine,
        IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags,
        IntPtr lpEnvironment, string lpCurrentDirectory, ref STARTUPINFO lpStartupInfo,
        out PROCESS_INFORMATION lpProcessInformation);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint ResumeThread(IntPtr hThread);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetExitCodeProcess(IntPtr hProcess, out int lpExitCode);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool TerminateProcess(IntPtr hProcess, uint uExitCode);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr hObject);
}
