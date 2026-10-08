// pipe_ipc primitive: pass a message through an anonymous pipe.
//
// Inter-process communication via an anonymous pipe: create the pipe, write a
// fixed message to the write end, read it back from the read end, verify it
// round-tripped. Exercises the pipe/read/write telemetry family. pipe() is the
// POSIX mechanism; CreatePipe is the Windows equivalent. This is the same pipe
// machinery a runtime's os/exec relay uses, so it is a natural substrate
// discriminator (the Go reverse-shell mover keys on exactly this).
//
// Self-contained and deterministic (its own pipe, fixed payload). The pipe API
// is raw platform code touching no C++ stdlib type, so the namespace-scope
// std::string below anchors libstdc++/libc++ into the binary; see
// empty/main.cpp for the full rationale.
#include <cstring>
#include <string>
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

#ifdef _WIN32
int main() {
    HANDLE rd, wr;
    if (!CreatePipe(&rd, &wr, nullptr, 0)) {
        return 1;
    }
    const char msg[] = "telemetry-lab\n";
    const DWORD n = static_cast<DWORD>(sizeof(msg) - 1);
    DWORD done = 0;
    if (!WriteFile(wr, msg, n, &done, nullptr) || done != n) {
        CloseHandle(rd);
        CloseHandle(wr);
        return 1;
    }
    char buf[sizeof(msg)];
    DWORD got = 0;
    if (!ReadFile(rd, buf, n, &got, nullptr) || got != n) {
        CloseHandle(rd);
        CloseHandle(wr);
        return 1;
    }
    CloseHandle(rd);
    CloseHandle(wr);
    return std::memcmp(buf, msg, n) == 0 ? 0 : 1;
}
#else
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
#endif
