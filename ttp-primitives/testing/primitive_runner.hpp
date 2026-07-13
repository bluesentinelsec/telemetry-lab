#pragma once

// Shared Catch2 support for the C and C++ primitive test suites.
//
// A primitive is measured as a standalone executable, so its main() cannot be
// linked into a test binary, and wrapping its logic in a library to make it
// linkable would add a call boundary to the very artifact under measurement.
// The tests therefore spawn the built primitive and assert on its exit code,
// which is the same shape the Go and Rust suites use.

#include <cstdlib>
#include <string>

#ifndef _WIN32
#include <sys/wait.h>
#endif

namespace telemetry_lab {

// Runs a primitive binary and returns its exit code, or -1 if it did not exit
// normally (killed by a signal, failed to launch).
inline int run_primitive(const std::string& path) {
    const std::string command = "\"" + path + "\"";
    const int status = std::system(command.c_str());

#ifdef _WIN32
    return status;
#else
    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return -1;
#endif
}

}  // namespace telemetry_lab
