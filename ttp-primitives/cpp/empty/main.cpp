#include <string>

// DESIGN CONCESSION (C++ standard-library axis).
//
// The C++ substrate axis compares the C++ standard library -- libstdc++ (GNU)
// vs libc++ (LLVM) -- holding the compiler (clang++) and the C runtime constant.
// That library is only linked when a program actually uses it. On Windows, a
// bare `int main(){ return 0; }` links NEITHER stdlib DLL, so the two configs
// would be indistinguishable for this primitive (confirmed on windows-2025:
// both import only the UCRT). On Linux the clang++ driver links libstdc++
// unconditionally, so this only bites on Windows -- but the primitive source is
// shared, so the fix lives here.
//
// The body references the C++ standard library so the stdlib is dynamically
// imported (libstdc++-6.dll / libc++.dll on Windows; libstdc++.so.6 /
// libc++.so.1 on Linux), making `empty` a valid discriminator for the axis. It
// stays behaviourally empty: no output, always exits 0. The argc-dependent size
// defeats constant-folding and the small-string optimization, forcing a real
// heap allocation through the standard library -- an out-of-line call the
// linker cannot elide.
//
// This is a deliberate deviation from the minimal-primitive principle, needed
// only for compute-only primitives like `empty`; primitives that do real work
// use the C++ stdlib naturally. Mirrors the Go cgo concession. See
// tools/substrate.toml (windows-cpp-*) and the dissertation limitations.
int main(int argc, char**) {
    std::string s(static_cast<std::size_t>(argc) + 64, 'x');
    return static_cast<int>(s.size()) - (argc + 64);
}
