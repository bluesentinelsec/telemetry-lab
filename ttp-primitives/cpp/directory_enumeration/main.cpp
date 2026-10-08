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
// Enumerate the same platform root as the C and Go implementations.
#include <filesystem>

int main() {
    std::error_code ec;
    int entries = 0;
#ifdef _WIN32
    const char* root = "C:\\";
#else
    const char* root = "/";
#endif
    for (const auto& entry : std::filesystem::directory_iterator(root, ec)) {
        (void)entry;
        entries++;
    }
    if (ec) {
        return 1;
    }
    return entries > 0 ? 0 : 1;
}
