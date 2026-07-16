using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Diagnostics.Symbols;

namespace Tmon.Core;

/// <summary>
/// Layer 2 — business logic. Resolves an ETW syscall handler *address* to a
/// routine name (e.g. <c>NtCreateFile</c>). ETW reports the kernel address of the
/// service routine, so we find the loaded kernel module that contains the
/// address, compute its RVA, and look the RVA up in that module's PDB (fetched
/// from the Microsoft symbol server and cached on disk).
///
/// Everything is best-effort: if symbols cannot be resolved the caller falls back
/// to the raw address, so capture never fails on account of naming. Not
/// thread-safe; the engine only calls it from the ETW consumer thread.
/// </summary>
public sealed class SyscallResolver : IDisposable
{
    private readonly SymbolReader? _reader;
    private readonly List<(ulong Base, string Path)> _modules = new();
    private readonly Dictionary<string, NativeSymbolModule?> _openModules =
        new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<ulong, string?> _cache = new();

    public bool Enabled => _reader is not null;

    public SyscallResolver(bool enabled)
    {
        if (!enabled) return;
        try
        {
            _reader = new SymbolReader(TextWriter.Null, SymbolPath.MicrosoftSymbolServerPath)
            {
                SecurityCheck = _ => true, // trust the MS symbol server PDBs
            };
            LoadKernelModules();
            // Pre-warm ntoskrnl on this (main) thread so the first syscall on the
            // consumer thread does not stall on a PDB download.
            var krnl = _modules.FirstOrDefault(m =>
                m.Path.EndsWith("ntoskrnl.exe", StringComparison.OrdinalIgnoreCase));
            if (krnl.Path is not null) OpenModule(krnl.Path);
        }
        catch
        {
            _reader = null;
        }
    }

    /// <summary>Returns the routine name for an address, or null if unresolved.</summary>
    public string? Resolve(ulong address)
    {
        if (_reader is null || address == 0) return null;
        if (_cache.TryGetValue(address, out var cached)) return cached;
        string? name = ResolveUncached(address);
        _cache[address] = name;
        return name;
    }

    private string? ResolveUncached(ulong address)
    {
        var module = ModuleFor(address);
        if (module is null) return null;
        try
        {
            var sym = OpenModule(module.Value.Path);
            if (sym is null) return null;
            uint rva = (uint)(address - module.Value.Base);
            string name = sym.FindNameForRva(rva);
            return string.IsNullOrEmpty(name) ? null : Clean(name);
        }
        catch
        {
            return null;
        }
    }

    // The module with the greatest base address not exceeding `address` (kernel
    // modules are laid out so this identifies the containing image).
    private (ulong Base, string Path)? ModuleFor(ulong address)
    {
        (ulong Base, string Path)? best = null;
        foreach (var m in _modules)
            if (m.Base <= address && (best is null || m.Base > best.Value.Base))
                best = m;
        return best;
    }

    private NativeSymbolModule? OpenModule(string path)
    {
        if (_openModules.TryGetValue(path, out var cached)) return cached;
        NativeSymbolModule? sym = null;
        try
        {
            string pdb = _reader!.FindSymbolFilePathForModule(path);
            if (pdb is not null) sym = _reader.OpenNativeSymbolFile(pdb);
        }
        catch
        {
            sym = null;
        }
        _openModules[path] = sym;
        return sym;
    }

    // FindNameForRva may return "module!func", "func", or "func+0x1a"; keep func.
    private static string Clean(string name)
    {
        int bang = name.IndexOf('!');
        if (bang >= 0) name = name[(bang + 1)..];
        int plus = name.IndexOf('+');
        if (plus >= 0) name = name[..plus];
        return name;
    }

    private void LoadKernelModules()
    {
        var bases = new IntPtr[1024];
        if (!EnumDeviceDrivers(bases, (uint)(bases.Length * IntPtr.Size), out uint needed))
            return;
        int count = Math.Min(bases.Length, (int)(needed / IntPtr.Size));
        var sb = new StringBuilder(1024);
        for (int i = 0; i < count; i++)
        {
            sb.Clear();
            if (GetDeviceDriverFileName(bases[i], sb, (uint)sb.Capacity) > 0)
                _modules.Add(((ulong)bases[i].ToInt64(), NormalizePath(sb.ToString())));
        }
    }

    // EnumDeviceDrivers reports NT-namespace paths (\SystemRoot\..., \??\...).
    private static string NormalizePath(string p)
    {
        string win = Environment.GetFolderPath(Environment.SpecialFolder.Windows);
        string root = Path.GetPathRoot(win) ?? @"C:\";
        if (p.StartsWith(@"\SystemRoot\", StringComparison.OrdinalIgnoreCase))
            return win + p[@"\SystemRoot".Length..];
        if (p.StartsWith(@"\??\", StringComparison.OrdinalIgnoreCase))
            return p[4..];
        if (p.StartsWith(@"\Windows\", StringComparison.OrdinalIgnoreCase))
            return root.TrimEnd('\\') + p;
        return p;
    }

    public void Dispose() => _reader?.Dispose();

    [DllImport("psapi.dll", SetLastError = true)]
    private static extern bool EnumDeviceDrivers(IntPtr[] lpImageBase, uint cb, out uint lpcbNeeded);

    [DllImport("psapi.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern uint GetDeviceDriverFileName(IntPtr ImageBase, StringBuilder lpFilename, uint nSize);
}
