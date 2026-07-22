// process_exec primitive: replace the current process image with a no-op.
//
// Distinct from `spawn` (which forks a child and reaps it): exec-family calls
// REPLACE the calling image in place, so no new pid is created and control
// never returns on success. This exercises the execve telemetry path without
// the fork/clone that spawn emits -- a different process-lifecycle signal.
//
// execlp searches PATH for `true`, whose only job is to exit 0; since exec
// replaces this image, that exit status becomes the primitive's. execlp returns
// only if the exec itself failed, in which case we exit non-zero.
//
// Raw POSIX exec touches no C++ standard-library type, so -- like `empty` -- it
// would not link libstdc++/libc++ and the C++ substrate axis would not
// manifest. The namespace-scope std::string below anchors the stdlib into the
// binary; see empty/main.cpp for the full rationale. (The anchor's destructor
// never runs here because exec replaces the image, but its presence still adds
// the NEEDED library at link time, which is what the axis measures.)
//
// Linux-only: Windows has no true exec-replace semantic (see issue #44).
#include <string>
#include <unistd.h>

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

int main() {
    execlp("true", "true", static_cast<char*>(nullptr));
    return 1;  // only reached if exec failed
}
