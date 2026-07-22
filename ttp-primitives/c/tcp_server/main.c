/* tcp_server primitive: accept a TCP connection and receive data.
 *
 * The measured behaviour is the server path: socket -> bind -> listen -> accept
 * -> recv -> send. A loopback client on 127.0.0.1 and an ephemeral port drives
 * the connection so the primitive is self-contained and offline. The exchange
 * is single-threaded: the client connects into the listen backlog, then the
 * server accepts, receives the request, and sends a reply. The client is
 * scaffolding; tcp_client is the primitive that emphasises it.
 *
 * Sockets are libc calls, so glibc vs musl is the axis under measurement.
 * Linux-only for this pass (Winsock on Windows -- issue #44). */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int main(void) {
    int lst = socket(AF_INET, SOCK_STREAM, 0);
    if (lst < 0) {
        return 1;
    }
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0; /* ephemeral */
    if (bind(lst, (struct sockaddr *)&addr, sizeof addr) != 0 || listen(lst, 1) != 0) {
        return 1;
    }
    socklen_t alen = sizeof addr;
    if (getsockname(lst, (struct sockaddr *)&addr, &alen) != 0) {
        return 1;
    }

    int cli = socket(AF_INET, SOCK_STREAM, 0);
    if (cli < 0 || connect(cli, (struct sockaddr *)&addr, sizeof addr) != 0) {
        return 1;
    }
    int srv = accept(lst, 0, 0);
    if (srv < 0) {
        return 1;
    }

    const char req[] = "telemetry-lab\n";
    const size_t n = sizeof(req) - 1;
    if (send(cli, req, n, 0) != (ssize_t)n) {
        return 1;
    }
    char buf[sizeof(req)];
    ssize_t got = recv(srv, buf, n, 0);
    if (got == (ssize_t)n) {
        send(srv, buf, (size_t)got, 0); /* echo reply */
    }

    close(cli);
    close(srv);
    close(lst);
    return got == (ssize_t)n ? 0 : 1;
}
