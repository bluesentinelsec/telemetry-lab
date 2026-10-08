/* dns_lookup primitive: resolve a hostname to addresses.
 *
 * Name resolution is a precursor to most network activity. getaddrinfo is the
 * standard resolver entry point; resolving "localhost" keeps the primitive
 * offline and deterministic (served from the hosts file, no DNS packet) while
 * still exercising the resolver telemetry path.
 *
 * On POSIX the resolver lives in libc, so this is a strong glibc-vs-musl
 * discriminator (NSS modules vs musl's built-in resolver) and where Go's
 * cgo/pure-Go split diverges most. On Windows getaddrinfo is provided by
 * Winsock (linking ws2_32). Exits 0 when resolution yields at least one
 * address. */
#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string.h>

int main(void) {
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        return 1;
    }
    struct addrinfo hints;
    struct addrinfo *res = 0;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo("localhost", "80", &hints, &res) != 0 || res == 0) {
        WSACleanup();
        return 1;
    }
    freeaddrinfo(res);
    WSACleanup();
    return 0;
}
#else
#include <netdb.h>
#include <string.h>

int main(void) {
    struct addrinfo hints;
    struct addrinfo *res = 0;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo("localhost", "80", &hints, &res) != 0 || res == 0) {
        return 1;
    }
    freeaddrinfo(res);
    return 0;
}
#endif
