/* directory_enumeration primitive: list the entries of a directory.
 *
 * Filesystem discovery -- listing a directory -- is a recurring reconnaissance
 * primitive. It exercises the directory-read telemetry path (openat + getdents)
 * distinctly from file_io's open/read/write of a single file. The root
 * directory "/" is always present and read-only here, so the primitive is
 * deterministic and needs no setup.
 *
 * Linux-only for this pass (portable via FindFirstFile / std::filesystem on
 * Windows -- issue #44). */
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
