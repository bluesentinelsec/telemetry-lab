// directory_enumeration primitive: list the entries of a directory.
//
// Filesystem discovery -- listing a directory -- is a recurring reconnaissance
// primitive. It exercises the directory-read telemetry path (openat + getdents)
// distinctly from file_io's open/read/write of a single file. The root
// directory "/" is always present and read-only here, so the primitive is
// deterministic and needs no setup.
//
// std::filesystem::directory_iterator is a C++ standard-library facility, so
// this primitive links libstdc++/libc++ naturally -- no explicit substrate
// anchor is needed (unlike the compute-only `empty`).
//
// Linux-only for this pass (portable via std::filesystem on Windows too, but
// gated with the rest of this pass -- issue #44).
#include <filesystem>

int main() {
    std::error_code ec;
    int entries = 0;
    for (const auto& entry : std::filesystem::directory_iterator("/", ec)) {
        (void)entry;
        entries++;
    }
    if (ec) {
        return 1;
    }
    return entries > 0 ? 0 : 1;
}
