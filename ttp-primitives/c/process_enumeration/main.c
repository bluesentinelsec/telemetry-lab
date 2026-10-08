/* process_enumeration primitive: enumerate running processes.
 *
 * Discovery of other processes is a ubiquitous post-compromise primitive. On
 * Linux the canonical mechanism is walking /proc: each numeric subdirectory is a
 * live pid. On Windows the equivalent is a Toolhelp process snapshot. Either way
 * the primitive exercises the process-table read path against the kernel rather
 * than any single process event.
 *
 * Self-contained and read-only: it counts the live processes and exits 0 as long
 * as at least itself is visible. */
#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>

int main(void) {
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
#include <ctype.h>
#include <dirent.h>

int main(void) {
    DIR *proc = opendir("/proc");
    if (!proc) {
        return 1;
    }
    int pids = 0;
    struct dirent *e;
    while ((e = readdir(proc)) != 0) {
        if (isdigit((unsigned char)e->d_name[0])) {
            pids++;
        }
    }
    closedir(proc);
    return pids > 0 ? 0 : 1;
}
#endif
