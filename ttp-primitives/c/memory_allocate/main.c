/* memory_allocate primitive: allocate, touch, and free a large buffer.
 *
 * Memory acquisition underlies staging, unpacking, and injection. The allocation
 * is deliberately large (64 MiB) so it exceeds glibc's mmap threshold and the
 * allocator services it with a fresh mmap rather than the heap free-list --
 * making the acquisition visible as an mmap/munmap telemetry pair. Each page is
 * touched so the mapping is actually faulted in, not just reserved.
 *
 * The allocator is part of the C runtime, so glibc vs musl is exactly the axis
 * under measurement here. Self-contained; frees before exit. */
#include <stdlib.h>
#include <string.h>

#define ALLOC_BYTES (64u * 1024u * 1024u)
#define PAGE 4096u

int main(void) {
    unsigned char *buf = malloc(ALLOC_BYTES);
    if (!buf) {
        return 1;
    }
    for (size_t i = 0; i < ALLOC_BYTES; i += PAGE) {
        buf[i] = (unsigned char)i;
    }
    free(buf);
    return 0;
}
