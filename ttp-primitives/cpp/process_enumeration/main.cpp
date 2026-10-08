// process_enumeration primitive: enumerate running processes.
//
// Discovery of other processes is a ubiquitous post-compromise primitive. On
// Linux the canonical mechanism is walking /proc: each numeric subdirectory is
// a live pid. On Windows the equivalent is a Toolhelp process snapshot. Either
// way the primitive exercises the process-table read path against the kernel
// rather than any single process event.
//
// Self-contained and read-only: it counts the live processes and exits 0 as
// long as at least itself is visible.
//
// The enumeration is raw platform API, touching no C++ stdlib type, so the
// namespace-scope std::string below anchors libstdc++/libc++ into the binary;
// see empty/main.cpp for the full rationale.
#include <string>
#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#else
#include <cctype>
#include <dirent.h>
#endif

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

#ifdef _WIN32
int main() {
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snap == INVALID_HANDLE_VALUE) {
        return 1;
    }
    PROCESSENTRY32 pe;
    pe.dwSize = sizeof pe;
    int procs = 0;
    if (Process32First(snap, &pe)) {
        do {
            procs++;
        } while (Process32Next(snap, &pe));
    }
    CloseHandle(snap);
    return procs > 0 ? 0 : 1;
}
#else
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
#endif
