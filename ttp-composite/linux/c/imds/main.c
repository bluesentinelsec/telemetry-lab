/* imds composite (ATT&CK T1552.005) -- EC2 Instance Metadata Service contact.
 *
 * A connect-seam probe: open a socket and connect to 169.254.169.254:80. Falco's
 * "Contact EC2 Instance Metadata Service From Container" keys on the connect
 * syscall's destination IP (fd.sip), not on success or on data read -- so it is
 * expected to be ROBUST across substrates (a connect is a connect). This is the
 * cross-engine seam-catalog entry: it tests whether the PoC's auditd Go
 * non-blocking-connect evasion (which filtered on success=1) generalizes to
 * Falco. IMDS is reachable in the AWS lab.
 *
 * Benign: it only opens a connection and closes it; no credentials are read.
 * Detonates in a container. */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int main(void) {
    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0) {
        return 1;
    }
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(80);
    inet_pton(AF_INET, "169.254.169.254", &addr.sin_addr);
    connect(s, (struct sockaddr *)&addr, sizeof addr); /* the fired syscall */
    close(s);
    return 0;
}
