"""Fact extraction for PE (Windows) binaries.

Not implemented yet: Linux is being confirmed end to end first.

When this lands it must populate the same fact keys the ELF extractor does, so
that the rule vocabulary and manifest format stay format-neutral:

    format   -> "pe"
    machine  -> "x86-64"
    needed   -> imported DLL names, which is where the CRT shows up:
                MSVC             -> VCRUNTIME140.dll + api-ms-win-crt-*.dll (UCRT)
                MinGW (msvcrt)   -> msvcrt.dll
                MinGW (ucrt)     -> api-ms-win-crt-*.dll
    linkage  -> "dynamic" / "static"
    comment  -> producing toolchain, recoverable from the PE Rich header

Note: a MinGW build is not automatically an MSVCRT build. The windows-2025
runner ships the UCRT flavor of mingw-w64, so its binaries import the same
api-ms-win-crt-* stubs MSVC does. Whichever flavor the lab pins, this extractor
is what proves it.
"""

MAGIC = b"MZ"


def matches(data):
    return data[:2] == MAGIC


def extract(data):
    raise NotImplementedError(
        "PE extraction is not implemented yet; Linux is being confirmed first"
    )
