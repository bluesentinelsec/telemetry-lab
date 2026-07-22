/* symlink_sensitive composite (ATT&CK T1555) -- symlink over a sensitive file.
 *
 * A robustness control (effect-keyed, expected to FIRE on every substrate).
 * Falco's "Create Symlink Over Sensitive Files" keys on a symlink whose target
 * is a sensitive path (/etc/shadow). Benign: the link is created in /tmp and
 * removed immediately; /etc/shadow itself is untouched. Detonates in a
 * container. */
#include <unistd.h>

int main(void) {
    unlink("/tmp/lab_shadow_link");
    if (symlink("/etc/shadow", "/tmp/lab_shadow_link") != 0) {
        return 1;
    }
    unlink("/tmp/lab_shadow_link");
    return 0;
}
