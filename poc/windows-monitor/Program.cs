// PoC Windows telemetry monitor: process-scoped ETW capture.
//
// Mirrors the Linux libbpf PoC's "spawn-and-trace" model:
//   1. Start a real-time kernel ETW session (process + image-load events).
//   2. CreateProcess the target SUSPENDED so we own its PID before it runs.
//   3. Seed the traced-PID set with the target, then ResumeThread.
//   4. In the consumer callback, record only events whose ProcessID is in the
//      traced set; grow the set to descendants via ProcessStart events.
//
// Unlike Linux (where the BPF program filters in-kernel), the Windows kernel
// session is system-wide, so scoping is enforced in the consumer -- but the
// result is the same: only the target process tree is recorded.

using System;
using System.Collections.Concurrent;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using Microsoft.Diagnostics.Tracing.Parsers;
using Microsoft.Diagnostics.Tracing.Parsers.Kernel;
using Microsoft.Diagnostics.Tracing.Session;

class Program
{
    static readonly ConcurrentDictionary<int, byte> Traced = new ConcurrentDictionary<int, byte>();
    static int _targetPid;
    static volatile bool _exited;

    const uint CREATE_SUSPENDED = 0x4;

    [StructLayout(LayoutKind.Sequential)]
    struct STARTUPINFO
    {
        public int cb;
        public IntPtr lpReserved, lpDesktop, lpTitle;
        public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public ushort wShowWindow, cbReserved2;
        public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct PROCESS_INFORMATION { public IntPtr hProcess, hThread; public int dwProcessId, dwThreadId; }

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    static extern bool CreateProcess(string lpApplicationName, StringBuilder lpCommandLine,
        IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags,
        IntPtr lpEnvironment, string lpCurrentDirectory, ref STARTUPINFO lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation);

    [DllImport("kernel32.dll", SetLastError = true)] static extern uint ResumeThread(IntPtr hThread);
    [DllImport("kernel32.dll", SetLastError = true)] static extern bool CloseHandle(IntPtr h);

    static void Main(string[] args)
    {
        if (args.Length < 1) { Console.Error.WriteLine("usage: monitor <command> [args...]"); return; }
        string cmdline = string.Join(" ", args);

        if (!(TraceEventSession.IsElevated() ?? false)) { Console.Error.WriteLine("must run elevated"); return; }

        using (var session = new TraceEventSession(KernelTraceEventParser.KernelSessionName))
        {
            session.EnableKernelProvider(
                KernelTraceEventParser.Keywords.Process |
                KernelTraceEventParser.Keywords.ImageLoad);

            var k = session.Source.Kernel;
            k.ProcessStart += (ProcessTraceData e) =>
            {
                if (Traced.ContainsKey(e.ParentID))
                {
                    Traced[e.ProcessID] = 1;
                    Console.WriteLine($"PROC-START pid={e.ProcessID,-6} ppid={e.ParentID,-6} {e.ImageFileName}");
                }
            };
            k.ProcessStop += (ProcessTraceData e) =>
            {
                if (Traced.ContainsKey(e.ProcessID))
                {
                    Console.WriteLine($"PROC-STOP  pid={e.ProcessID,-6} {e.ImageFileName}");
                    if (e.ProcessID == _targetPid) _exited = true;
                    byte tmp; Traced.TryRemove(e.ProcessID, out tmp);
                }
            };
            k.ImageLoad += (ImageLoadTraceData e) =>
            {
                if (Traced.ContainsKey(e.ProcessID))
                    Console.WriteLine($"IMAGE      pid={e.ProcessID,-6} {e.FileName}");
            };

            var consumer = new Thread(() => session.Source.Process()) { IsBackground = true };
            consumer.Start();
            Thread.Sleep(1000); // let the session start consuming before we launch

            var si = new STARTUPINFO(); si.cb = Marshal.SizeOf<STARTUPINFO>();
            PROCESS_INFORMATION pi;
            if (!CreateProcess(null, new StringBuilder(cmdline), IntPtr.Zero, IntPtr.Zero, false,
                    CREATE_SUSPENDED, IntPtr.Zero, null, ref si, out pi))
            {
                Console.Error.WriteLine($"CreateProcess failed: {Marshal.GetLastWin32Error()}");
                return;
            }
            _targetPid = pi.dwProcessId;
            Traced[_targetPid] = 1;
            Console.Error.WriteLine($"[monitor] tracing target pid={_targetPid}: {cmdline}");

            ResumeThread(pi.hThread);

            int waited = 0;
            while (!_exited && waited < 30000) { Thread.Sleep(50); waited += 50; }
            Thread.Sleep(500); // drain buffered events

            CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
        }
    }
}
