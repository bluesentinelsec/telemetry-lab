/* http_client primitive: perform HTTP GET and POST requests.
 *
 * HTTP is the most common application-layer channel for staging and C2. The
 * request/response is hand-rolled over a raw TCP socket -- no HTTP or TLS
 * library -- so the primitive adds no third-party runtime and works on every
 * substrate including musl and static builds (see issue #43 for why the TLS
 * https_client is deferred). It stays self-contained and offline by talking to
 * a loopback responder on 127.0.0.1 and an ephemeral port, single-threaded via
 * the listen backlog. Both a GET and a POST are issued to exercise both methods.
 *
 * At the syscall level this is the tcp_client path plus HTTP framing in the
 * payload; the point is the request/response round-trip, not a full HTTP client.
 * Linux-only for this pass (Winsock on Windows -- issue #44). */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

/* One full HTTP exchange over loopback: client sends `request`, server reads it
 * and replies, client reads the reply. Both ends stay open throughout, so no
 * send races a closed peer. Returns 0 on success. */
static int exchange(int lst, const struct sockaddr_in *addr, const char *request) {
    int cli = socket(AF_INET, SOCK_STREAM, 0);
    if (cli < 0) {
        return 1;
    }
    if (connect(cli, (const struct sockaddr *)addr, sizeof *addr) != 0) {
        close(cli);
        return 1;
    }
    int srv = accept(lst, 0, 0);
    if (srv < 0) {
        close(cli);
        return 1;
    }

    size_t rn = strlen(request);
    int ok = send(cli, request, rn, 0) == (ssize_t)rn;

    char buf[512];
    if (ok) {
        ok = recv(srv, buf, sizeof buf, 0) > 0; /* server reads the request */
    }
    if (ok) {
        const char *resp = "HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok";
        size_t sn = strlen(resp);
        ok = send(srv, resp, sn, 0) == (ssize_t)sn;
    }
    if (ok) {
        ok = recv(cli, buf, sizeof buf, 0) > 0; /* client reads the response */
    }

    close(srv);
    close(cli);
    return ok ? 0 : 1;
}

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
    if (bind(lst, (struct sockaddr *)&addr, sizeof addr) != 0 || listen(lst, 2) != 0) {
        return 1;
    }
    socklen_t alen = sizeof addr;
    if (getsockname(lst, (struct sockaddr *)&addr, &alen) != 0) {
        return 1;
    }

    const char *get = "GET / HTTP/1.0\r\nHost: localhost\r\n\r\n";
    const char *post = "POST / HTTP/1.0\r\nHost: localhost\r\n"
                       "Content-Length: 14\r\n\r\ntelemetry-lab\n";

    int rc = exchange(lst, &addr, get);
    if (rc == 0) {
        rc = exchange(lst, &addr, post);
    }
    close(lst);
    return rc;
}
