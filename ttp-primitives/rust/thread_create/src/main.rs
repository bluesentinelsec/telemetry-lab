//! thread_create primitive: create one worker thread and join it.
//!
//! Thread creation exercises the kernel's clone/thread telemetry path (a new
//! task sharing the address space, as opposed to spawn's separate process). The
//! worker does nothing; the point is the create/join lifecycle, not the work.
//!
//! `std::thread::spawn` maps onto the platform thread primitive (clone/pthread
//! on Linux), which lives in libc, so the substrate (glibc vs musl) is what
//! varies. Portable across platforms via std::thread (Windows -- issue #44).

use std::thread;

fn main() {
    let handle = thread::spawn(|| {});
    handle.join().expect("join worker thread");
}
