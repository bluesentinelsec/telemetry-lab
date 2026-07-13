"""Fact extraction for ELF binaries, using only the standard library.

Deliberately avoids pyelftools and binutils. The verifier has to run unchanged
against artifacts pulled back from a lab host, where nothing may be installed,
and `ldd` in particular is unusable here: the host's glibc ldd errors out with
"invalid ELF header" when handed a musl-linked binary.
"""

import struct

PT_INTERP = 3
SHT_DYNAMIC = 6
DT_NULL = 0
DT_NEEDED = 1

MACHINES = {0x3E: "x86-64", 0xB7: "aarch64"}

MAGIC = b"\x7fELF"


def matches(data):
    return data[:4] == MAGIC


def _u16(data, off):
    return struct.unpack_from("<H", data, off)[0]


def _u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def _u64(data, off):
    return struct.unpack_from("<Q", data, off)[0]


def _program_headers(data):
    e_phoff = _u64(data, 0x20)
    e_phentsize = _u16(data, 0x36)
    e_phnum = _u16(data, 0x38)
    for i in range(e_phnum):
        yield e_phoff + i * e_phentsize


def _section_headers(data):
    e_shoff = _u64(data, 0x28)
    e_shentsize = _u16(data, 0x3A)
    e_shnum = _u16(data, 0x3C)
    for i in range(e_shnum):
        yield e_shoff + i * e_shentsize


def _section_names(data):
    """Map section name -> (offset, size, type, link)."""
    e_shstrndx = _u16(data, 0x3E)
    e_shoff = _u64(data, 0x28)
    e_shentsize = _u16(data, 0x3A)

    strtab_hdr = e_shoff + e_shstrndx * e_shentsize
    strtab_off = _u64(data, strtab_hdr + 24)

    sections = {}
    for hdr in _section_headers(data):
        name_off = _u32(data, hdr + 0)
        end = data.index(b"\x00", strtab_off + name_off)
        name = data[strtab_off + name_off:end].decode("utf-8", "replace")
        sections[name] = {
            "type": _u32(data, hdr + 4),
            "offset": _u64(data, hdr + 24),
            "size": _u64(data, hdr + 32),
            "link": _u32(data, hdr + 40),
            "index": hdr,
        }
    return sections


def _interpreter(data):
    """The dynamic loader this binary requests. None means statically linked.

    This is the decisive glibc/musl discriminator: glibc requests
    /lib64/ld-linux-x86-64.so.2, musl requests /lib/ld-musl-x86_64.so.1.
    """
    for hdr in _program_headers(data):
        if _u32(data, hdr) == PT_INTERP:
            offset = _u64(data, hdr + 8)
            size = _u64(data, hdr + 32)
            return data[offset:offset + size].rstrip(b"\x00").decode("utf-8", "replace")
    return None


def _needed(data, sections):
    """DT_NEEDED entries: the shared libraries this binary links against."""
    dynamic = next(
        (s for s in sections.values() if s["type"] == SHT_DYNAMIC),
        None,
    )
    if dynamic is None:
        return []

    # sh_link on .dynamic names the string table its entries index into.
    e_shoff = _u64(data, 0x28)
    e_shentsize = _u16(data, 0x3A)
    strtab_hdr = e_shoff + dynamic["link"] * e_shentsize
    strtab_off = _u64(data, strtab_hdr + 24)

    needed = []
    off = dynamic["offset"]
    while off < dynamic["offset"] + dynamic["size"]:
        d_tag = _u64(data, off)
        d_val = _u64(data, off + 8)
        if d_tag == DT_NULL:
            break
        if d_tag == DT_NEEDED:
            end = data.index(b"\x00", strtab_off + d_val)
            needed.append(data[strtab_off + d_val:end].decode("utf-8", "replace"))
        off += 16
    return needed


def _comment(data, sections):
    """The .comment section carries the producing toolchain's version string.

    Note this identifies the *compiler*, not the libc: musl-gcc is a wrapper
    around the same gcc, so glibc and musl builds emit an identical string.
    """
    section = sections.get(".comment")
    if section is None:
        return None
    raw = data[section["offset"]:section["offset"] + section["size"]]
    parts = [p.decode("utf-8", "replace") for p in raw.split(b"\x00") if p]
    return "; ".join(parts) if parts else None


def extract(data):
    if data[4] != 2:
        raise ValueError("only 64-bit ELF is supported")
    if data[5] != 1:
        raise ValueError("only little-endian ELF is supported")

    sections = _section_names(data)
    interpreter = _interpreter(data)
    needed = _needed(data, sections)

    return {
        "format": "elf",
        "machine": MACHINES.get(_u16(data, 0x12), hex(_u16(data, 0x12))),
        "interpreter": interpreter,
        "needed": needed,
        "linkage": "static" if interpreter is None and not needed else "dynamic",
        "comment": _comment(data, sections),
    }
