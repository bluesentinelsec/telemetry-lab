"""Fact extraction for PE (Windows) binaries, using only the standard library.

Populates the same format-neutral fact keys the ELF extractor does, so the rule
vocabulary and manifest stay format-agnostic:

    format   -> "pe"
    machine  -> "x86-64"
    needed   -> imported DLL names (the import table), where the CRT shows up
    linkage  -> "dynamic" if the CRT is imported, "static" if linked in
    libc     -> the C runtime: "UCRT" or "MSVCRT"
    comment  -> None (PE has no direct analogue of ELF .comment)

The CRT identity is read from the import table, which is the authoritative
record of what the linker bound: a UCRT build imports api-ms-win-crt-*.dll (and,
under MSVC, VCRUNTIME140.dll); an MSVCRT build imports msvcrt.dll. This is the
Windows analogue of reading DT_NEEDED / the ELF interpreter on Linux.
"""

import struct

MACHINES = {0x8664: "x86-64", 0x14C: "i386", 0xAA64: "aarch64"}

MAGIC = b"MZ"


def matches(data):
    return data[:2] == MAGIC


def _u16(data, off):
    return struct.unpack_from("<H", data, off)[0]


def _u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def _sections(data, sec_off, count):
    """Yield (virtual_address, raw_size, raw_pointer) for each section."""
    for i in range(count):
        base = sec_off + i * 40
        virtual_address = _u32(data, base + 12)
        raw_size = _u32(data, base + 16)
        raw_pointer = _u32(data, base + 20)
        yield virtual_address, raw_size, raw_pointer


def _rva_to_offset(rva, sections):
    for virtual_address, raw_size, raw_pointer in sections:
        if virtual_address <= rva < virtual_address + max(raw_size, 1):
            return raw_pointer + (rva - virtual_address)
    return None


def _cstr(data, offset):
    end = data.index(b"\x00", offset)
    return data[offset:end].decode("ascii", "replace")


def _imports(data):
    """Return the list of imported DLL names, lowercased, in table order."""
    e_lfanew = _u32(data, 0x3C)
    if data[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        raise ValueError("not a PE image")

    coff = e_lfanew + 4
    num_sections = _u16(data, coff + 2)
    opt_size = _u16(data, coff + 16)
    opt = coff + 20

    magic = _u16(data, opt)
    if magic == 0x20B:        # PE32+
        dir_base = opt + 112
    elif magic == 0x10B:      # PE32
        dir_base = opt + 96
    else:
        raise ValueError(f"unknown optional header magic {magic:#x}")

    # Data directory index 1 is the import table.
    import_rva = _u32(data, dir_base + 1 * 8)
    if import_rva == 0:
        return []

    sections = list(_sections(data, opt + opt_size, num_sections))
    table = _rva_to_offset(import_rva, sections)
    if table is None:
        return []

    names = []
    entry = table
    while True:
        name_rva = _u32(data, entry + 12)
        if name_rva == 0 and _u32(data, entry) == 0:
            break  # null terminator descriptor
        if name_rva:
            name_off = _rva_to_offset(name_rva, sections)
            if name_off is not None:
                names.append(_cstr(data, name_off).lower())
        entry += 20
        if entry + 20 > len(data):
            break
    return names


def _crt(needed):
    """Identify the C runtime from the imported DLLs.

    UCRT: the app-facing CRT is the api-ms-win-crt-* umbrella (and MSVC adds
    VCRUNTIME140.dll). MSVCRT: the legacy msvcrt.dll. Checked so that a build
    importing both would read as UCRT, but in practice they are exclusive.
    """
    if any(n.startswith("api-ms-win-crt-") or n == "vcruntime140.dll" or n == "ucrtbase.dll" for n in needed):
        return "UCRT"
    if "msvcrt.dll" in needed:
        return "MSVCRT"
    return None


def extract(data):
    machine = MACHINES.get(_u16(data, _u32(data, 0x3C) + 4), None)
    needed = _imports(data)
    crt = _crt(needed)

    return {
        "format": "pe",
        "machine": machine or hex(_u16(data, _u32(data, 0x3C) + 4)),
        "interpreter": None,
        "needed": needed,
        # The CRT is dynamically imported unless it was linked in statically.
        "linkage": "dynamic" if crt is not None else "static",
        "comment": None,
        "libc": crt,
    }
