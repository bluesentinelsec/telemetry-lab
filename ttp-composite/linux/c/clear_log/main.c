/* clear_log composite (ATT&CK T1070) -- truncate a file under /var/log.
 *
 * A robustness control (effect-keyed, expected to FIRE on every substrate).
 * Falco's "Clear Log Activities" keys on opening a file in a log directory with
 * truncation. Benign: it creates and truncates its own file under /var/log and
 * removes it -- no real log is destroyed. Detonates in a container. */
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    int fd = open("/var/log/lab_clear.log", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        return 1;
    }
    close(fd);
    unlink("/var/log/lab_clear.log");
    return 0;
}
