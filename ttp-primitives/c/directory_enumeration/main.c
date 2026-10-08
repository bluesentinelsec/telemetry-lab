/* directory_enumeration primitive: list the entries of a directory.
 *
 * Filesystem discovery -- listing a directory -- is a recurring reconnaissance
 * primitive. It exercises the directory-read telemetry path distinctly from
 * file_io's open/read/write of a single file. A well-known root directory ("/"
 * on POSIX, the C: drive root on Windows) is always present and read-only here,
 * so the primitive is deterministic and needs no setup. */
#ifdef _WIN32
#include <windows.h>

int main(void) {
    WIN32_FIND_DATA fd;
    HANDLE h = FindFirstFile("C:\\*", &fd);
    if (h == INVALID_HANDLE_VALUE) {
        return 1;
    }
    int entries = 0;
    do {
        entries++;
    } while (FindNextFile(h, &fd));
    FindClose(h);
    return entries > 0 ? 0 : 1;
}
#else
#include <dirent.h>

int main(void) {
    DIR *d = opendir("/");
    if (!d) {
        return 1;
    }
    int entries = 0;
    struct dirent *e;
    while ((e = readdir(d)) != 0) {
        entries++;
    }
    closedir(d);
    return entries > 0 ? 0 : 1;
}
#endif
