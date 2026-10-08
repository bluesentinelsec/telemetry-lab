/* thread_create primitive: create one worker thread and join it.
 *
 * Thread creation exercises the kernel's thread-lifecycle telemetry path (a new
 * task sharing the address space, as opposed to spawn's separate process). The
 * worker does nothing; the point is the create/join lifecycle, not the work.
 * pthread on POSIX and CreateThread on Windows are the native thread primitives;
 * both link the platform runtime naturally, so the substrate is what varies. */
#ifdef _WIN32
#include <windows.h>

static DWORD WINAPI worker(LPVOID arg) {
    (void)arg;
    return 0;
}

int main(void) {
    HANDLE t = CreateThread(NULL, 0, worker, NULL, 0, NULL);
    if (t == NULL) {
        return 1;
    }
    if (WaitForSingleObject(t, INFINITE) != WAIT_OBJECT_0) {
        CloseHandle(t);
        return 1;
    }
    CloseHandle(t);
    return 0;
}
#else
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
#endif
