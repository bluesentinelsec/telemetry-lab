/* mkdir_bin composite (ATT&CK T1222.002) -- create a directory in a binary path.
 *
 * A robustness control (effect-keyed, expected to FIRE on every substrate).
 * Falco's "Mkdir binary dirs" keys on creating a directory under a system
 * binary path (e.g. /usr/bin). Benign: the directory is empty and removed
 * immediately. Detonates in a container. */
#include <sys/stat.h>
#include <unistd.h>

int main(void) {
    rmdir("/usr/bin/lab_testdir");
    if (mkdir("/usr/bin/lab_testdir", 0755) != 0) {
        return 1;
    }
    rmdir("/usr/bin/lab_testdir");
    return 0;
}
