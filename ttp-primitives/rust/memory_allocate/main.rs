//! memory_allocate primitive: allocate, touch, and free a large buffer.
//!
//! Memory acquisition underlies staging, unpacking, and injection. The
//! allocation is deliberately large (64 MiB) so it exceeds the allocator's mmap
//! threshold and is serviced by a fresh mmap rather than the heap free-list --
//! making the acquisition visible as an mmap/munmap telemetry pair. Each page is
//! touched so the mapping is actually faulted in, not just reserved.
//!
//! The allocator is part of the runtime backing libc, so glibc vs musl is
//! exactly the axis under measurement here. Self-contained; the buffer is
//! dropped (freed) before exit.

use std::hint::black_box;

const ALLOC_BYTES: usize = 64 << 20; // 64 MiB
const PAGE: usize = 4096;

fn main() {
    let mut buf = vec![0u8; ALLOC_BYTES];
    let mut i = 0;
    while i < ALLOC_BYTES {
        buf[i] = i as u8;
        i += PAGE;
    }
    // Prevent the allocation + touch loop from being optimised away.
    black_box(&buf);
    drop(buf);
}
