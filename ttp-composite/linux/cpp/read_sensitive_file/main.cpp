// read_sensitive_file composite (ATT&CK T1555) -- read /etc/shadow.
//
// A robustness control: an effect-keyed technique that should FIRE across every
// substrate. Falco's "Read sensitive file untrusted" keys on an open-for-read of
// a known-sensitive path (/etc/shadow), which is the same syscall regardless of
// the runtime that issues it -- so no substrate should flip it. Benign: it reads
// a few bytes and closes. Runs as root in the container, where /etc/shadow is
// readable. Detonates in a container.
#include <fcntl.h>
#include <unistd.h>

int main() {
    int fd = open("/etc/shadow", O_RDONLY);
    if (fd < 0) {
        return 1;
    }
    char buf[64];
    read(fd, buf, sizeof buf);
    close(fd);
    return 0;
}
