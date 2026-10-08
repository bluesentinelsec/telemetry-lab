/* tcp_client primitive: open a TCP connection and send data.
 *
 * The measured behaviour is the client path: socket -> connect -> send -> recv.
 * To stay self-contained and offline, the primitive also opens a loopback
 * listener on 127.0.0.1 and an ephemeral port and drives the exchange against
 * itself -- no external host, no fixed port. A blocking connect to a listening
 * socket completes via the kernel's accept backlog, so the whole exchange runs
 * single-threaded (no thread-creation telemetry to confound the socket path).
 * The listener is scaffolding; tcp_server is the primitive that emphasises it.
 *
 * Sockets are libc calls on POSIX (glibc vs musl is the axis) and Winsock on
 * Windows (linking ws2_32). */
#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string.h>

int main(void) {
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        return 1;
    }
    SOCKET lst = socket(AF_INET, SOCK_STREAM, 0);
    if (lst == INVALID_SOCKET) {
        WSACleanup();
        return 1;
    }
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0; /* ephemeral */
    if (bind(lst, (struct sockaddr *)&addr, sizeof addr) != 0 || listen(lst, 1) != 0) {
        closesocket(lst);
        WSACleanup();
        return 1;
    }
    int alen = sizeof addr;
    if (getsockname(lst, (struct sockaddr *)&addr, &alen) != 0) {
        closesocket(lst);
        WSACleanup();
        return 1;
    }

    SOCKET cli = socket(AF_INET, SOCK_STREAM, 0);
    if (cli == INVALID_SOCKET || connect(cli, (struct sockaddr *)&addr, sizeof addr) != 0) {
        closesocket(lst);
        WSACleanup();
        return 1;
    }
    SOCKET srv = accept(lst, 0, 0);
    if (srv == INVALID_SOCKET) {
        closesocket(cli);
        closesocket(lst);
        WSACleanup();
        return 1;
    }

    const char msg[] = "telemetry-lab\n";
    const int n = (int)(sizeof(msg) - 1);
    if (send(cli, msg, n, 0) != n) {
        closesocket(srv);
        closesocket(cli);
        closesocket(lst);
        WSACleanup();
        return 1;
    }
    char buf[sizeof(msg)];
    int got = recv(srv, buf, n, 0);

    closesocket(cli);
    closesocket(srv);
    closesocket(lst);
    WSACleanup();
    return got == n ? 0 : 1;
}
#else
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

    const char msg[] = "telemetry-lab\n";
    const size_t n = sizeof(msg) - 1;
    if (send(cli, msg, n, 0) != (ssize_t)n) {
        return 1;
    }
    char buf[sizeof(msg)];
    ssize_t got = recv(srv, buf, n, 0);

    close(cli);
    close(srv);
    close(lst);
    return got == (ssize_t)n ? 0 : 1;
}
#endif
