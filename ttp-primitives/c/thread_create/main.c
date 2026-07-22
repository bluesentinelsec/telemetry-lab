/* thread_create primitive: create one worker thread and join it.
 *
 * Thread creation exercises the kernel's clone/thread telemetry path (a new task
 * sharing the address space, as opposed to spawn's separate process). The worker
 * does nothing; the point is the create/join lifecycle, not the work.
 *
 * pthread is the portable POSIX thread API; on modern glibc and on musl the
 * pthread implementation lives in libc itself, so no separate NEEDED library is
 * added and the substrate (glibc vs musl) is what varies.
 *
 * Linux-only for this pass (portable via std::thread on Windows -- issue #44). */
#include <pthread.h>

static void *worker(void *arg) {
    (void)arg;
    return 0;
}

int main(void) {
    pthread_t t;
    if (pthread_create(&t, 0, worker, 0) != 0) {
        return 1;
    }
    if (pthread_join(t, 0) != 0) {
        return 1;
    }
    return 0;
}
