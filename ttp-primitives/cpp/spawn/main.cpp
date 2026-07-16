// spawn primitive: create a child process and wait for it.
//
// Process creation via std::system. Like `empty`, a compute/C-runtime-only
// program would not link the C++ standard library, so the Windows C++ substrate
// axis (libstdc++ vs libc++) would not manifest; the namespace-scope
// std::string below anchors the stdlib into the binary (its non-trivial
// destructor runs at teardown and cannot be elided). The invoked no-op command
// differs per OS but the behaviour -- create and reap a child -- is equivalent.
// Exits 0 on success.
#include <cstdlib>
#include <string>

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

int main() {
#ifdef _WIN32
    return std::system("cmd /c exit 0") != 0;
#else
    return std::system("true") != 0;
#endif
}
