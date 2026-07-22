/* process_exec primitive: replace the current process image with a no-op.
 *
 * Distinct from `spawn` (which forks a child and reaps it): exec-family calls
 * REPLACE the calling image in place, so no new pid is created and control never
 * returns on success. This exercises the execve telemetry path without the
 * fork/clone that spawn emits -- a different process-lifecycle signal.
 *
 * execlp searches PATH for `true`, whose only job is to exit 0; since exec
 * replaces this image, that exit status becomes the primitive's. execlp returns
 * only if the exec itself failed, in which case we exit non-zero.
 *
 * Linux-only: Windows has no true exec-replace semantic (see issue #44). */
#include <unistd.h>

int main(void) {
    execlp("true", "true", (char *)0);
    return 1; /* only reached if exec failed */
}
