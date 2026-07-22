/* process_enumeration primitive: enumerate running processes.
 *
 * Discovery of other processes is a ubiquitous post-compromise primitive. On
 * Linux the canonical mechanism is walking /proc: each numeric subdirectory is a
 * live pid. This exercises the directory-read telemetry path against the kernel's
 * process table (openat/getdents on /proc) rather than any single process event.
 *
 * Self-contained and read-only: it counts the numeric entries and exits 0 as
 * long as at least itself is visible.
 *
 * Linux-only: Windows enumerates via Toolhelp32Snapshot (see issue #44). */
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
