// thread_create primitive: create one worker thread and join it.
//
// Thread creation exercises the kernel's clone/thread telemetry path (a new
// task sharing the address space, as opposed to spawn's separate process). The
// worker does nothing; the point is the create/join lifecycle, not the work.
//
// std::thread is the C++ standard-library thread facility, so this primitive
// links libstdc++/libc++ naturally -- no explicit substrate anchor is needed
// (unlike the compute-only `empty`). On Linux std::thread is implemented over
// pthreads in libc, so the substrate (glibc vs musl) still varies underneath.
//
// Linux-only for this pass (portable via std::thread on Windows -- issue #44).
#include <thread>

int main() {
    std::thread t([] {});
    t.join();
    return 0;
}
