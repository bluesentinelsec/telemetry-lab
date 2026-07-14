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
// The namespace-scope std::string below anchors the C++ standard library into
// the binary: its non-trivial constructor and destructor run during runtime
// startup and teardown, so the stdlib DLL is dynamically imported
// (libstdc++-6.dll / libc++.dll on Windows; libstdc++.so.6 / libc++.so.1 on
// Linux) without any logic in main(). A local `std::string s;` does NOT suffice
// -- the optimizer elides an unused local and drops the import (confirmed on
// windows-2025); a global with a non-trivial destructor cannot be elided. The
// primitive stays behaviourally empty: no output, always exits 0.
//
// This is a deliberate deviation from the minimal-primitive principle, needed
// only for compute-only primitives like `empty`; primitives that do real work
// use the C++ stdlib naturally. Mirrors the Go cgo concession. See
// tools/substrate.toml (windows-cpp-*) and the dissertation limitations.
std::string stdlib_anchor;

int main() {
    return 0;
}
