/* spawn primitive: create a child process and wait for it.
 *
 * Process creation is the most ubiquitous adversary primitive and exercises the
 * process-lifecycle telemetry family (and the monitor's process-tree following).
 * system() is the portable way to spawn a child in C; the invoked no-op command
 * differs per OS but the behaviour -- create and reap a child process -- is
 * equivalent. Links the C runtime naturally, so no substrate anchor is needed.
 * Exits 0 on success. */
#include <stdlib.h>

int main(void) {
#ifdef _WIN32
    return system("cmd /c exit 0") != 0;
#else
    return system("true") != 0;
#endif
}
