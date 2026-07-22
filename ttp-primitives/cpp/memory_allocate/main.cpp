// memory_allocate primitive: allocate, touch, and free a large buffer.
//
// Memory acquisition underlies staging, unpacking, and injection. The
// allocation is deliberately large (64 MiB) so it exceeds the allocator's mmap
// threshold and is serviced with a fresh mmap rather than the heap free-list --
// making the acquisition visible as an mmap/munmap telemetry pair. Each page is
// touched so the mapping is actually faulted in, not just reserved.
//
// std::vector<char> is the C++ standard-library dynamic buffer, so this
// primitive links libstdc++/libc++ naturally -- no explicit substrate anchor is
// needed (unlike the compute-only `empty`). The vector's underlying allocator
// bottoms out in the C runtime, so glibc vs musl remains an axis in play too.
// Self-contained; the buffer is freed when the vector goes out of scope.
#include <vector>

namespace {
constexpr std::size_t kAllocBytes = 64u * 1024u * 1024u;
constexpr std::size_t kPage = 4096u;
}  // namespace

int main() {
    std::vector<char> buf(kAllocBytes);
    for (std::size_t i = 0; i < kAllocBytes; i += kPage) {
        buf[i] = static_cast<char>(i);
    }
    return 0;
}
