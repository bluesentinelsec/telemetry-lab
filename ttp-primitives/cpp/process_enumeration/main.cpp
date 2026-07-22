// process_enumeration primitive: enumerate running processes.
//
// Discovery of other processes is a ubiquitous post-compromise primitive. On
// Linux the canonical mechanism is walking /proc: each numeric subdirectory is
// a live pid. This exercises the directory-read telemetry path against the
// kernel's process table (openat/getdents on /proc) rather than any single
// process event.
//
// Self-contained and read-only: it counts the numeric entries and exits 0 as
// long as at least itself is visible.
//
// The /proc walk is raw POSIX (opendir/readdir), touching no C++ stdlib type,
// so the namespace-scope std::string below anchors libstdc++/libc++ into the
// binary; see empty/main.cpp for the full rationale.
//
// Linux-only: Windows enumerates via Toolhelp32Snapshot (see issue #44).
#include <cctype>
#include <string>
#include <dirent.h>

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

int main() {
    DIR* proc = opendir("/proc");
    if (!proc) {
        return 1;
    }
    int pids = 0;
    struct dirent* e;
    while ((e = readdir(proc)) != nullptr) {
        if (std::isdigit(static_cast<unsigned char>(e->d_name[0]))) {
            pids++;
        }
    }
    closedir(proc);
    return pids > 0 ? 0 : 1;
}
