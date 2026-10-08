/* pipe_ipc primitive: pass a message through an anonymous pipe.
 *
 * Inter-process communication via an anonymous pipe: create the pipe, write a
 * fixed message to the write end, read it back from the read end, verify it
 * round-tripped. Exercises the pipe/read/write telemetry family. pipe() is the
 * POSIX mechanism; CreatePipe is the Windows equivalent. This is the same pipe
 * machinery a runtime's os/exec relay uses, so it is a natural substrate
 * discriminator (the Go reverse-shell mover keys on exactly this).
 *
 * Self-contained and deterministic (its own pipe, fixed payload). */
#ifdef _WIN32
#include <windows.h>
#include <string.h>

int main(void) {
    HANDLE rd, wr;
    if (!CreatePipe(&rd, &wr, NULL, 0)) {
        return 1;
    }
    const char msg[] = "telemetry-lab\n";
    const DWORD n = (DWORD)(sizeof(msg) - 1);
    DWORD done = 0;
    if (!WriteFile(wr, msg, n, &done, NULL) || done != n) {
        CloseHandle(rd);
        CloseHandle(wr);
        return 1;
    }
    char buf[sizeof(msg)];
    DWORD got = 0;
    if (!ReadFile(rd, buf, n, &got, NULL) || got != n) {
        CloseHandle(rd);
        CloseHandle(wr);
        return 1;
    }
    CloseHandle(rd);
    CloseHandle(wr);
    return memcmp(buf, msg, n) == 0 ? 0 : 1;
}
#else
#include <string.h>
#include <unistd.h>

int main(void) {
    int fds[2];
    if (pipe(fds) != 0) {
        return 1;
    }
    const char msg[] = "telemetry-lab\n";
    const size_t n = sizeof(msg) - 1;
    if (write(fds[1], msg, n) != (ssize_t)n) {
        return 1;
    }
    char buf[sizeof(msg)];
    if (read(fds[0], buf, n) != (ssize_t)n) {
        return 1;
    }
    close(fds[0]);
    close(fds[1]);
    return memcmp(buf, msg, n) == 0 ? 0 : 1;
}
#endif
