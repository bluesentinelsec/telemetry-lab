// pipe_ipc primitive: pass a message through an anonymous pipe.
//
// Inter-process communication via an anonymous pipe: create the pipe, write a
// fixed message to the write end, read it back from the read end, verify it
// round-tripped. Exercises the pipe/read/write telemetry family. This is the
// same pipe machinery a runtime's os/exec relay uses, so it is a natural
// substrate discriminator (the Go reverse-shell mover keys on exactly this).
//
// Self-contained and deterministic (its own pipe, fixed payload). pipe() is
// raw POSIX and touches no C++ stdlib type, so the namespace-scope std::string
// below anchors libstdc++/libc++ into the binary; see empty/main.cpp for the
// full rationale.
//
// Linux-only: Windows uses CreatePipe/_pipe (issue #44).
#include <cstring>
#include <string>
#include <unistd.h>

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

int main() {
    int fds[2];
    if (pipe(fds) != 0) {
        return 1;
    }
    const char msg[] = "telemetry-lab\n";
    const std::size_t n = sizeof(msg) - 1;
    if (write(fds[1], msg, n) != static_cast<ssize_t>(n)) {
        return 1;
    }
    char buf[sizeof(msg)];
    if (read(fds[0], buf, n) != static_cast<ssize_t>(n)) {
        return 1;
    }
    close(fds[0]);
    close(fds[1]);
    return std::memcmp(buf, msg, n) == 0 ? 0 : 1;
}
