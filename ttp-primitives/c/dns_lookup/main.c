/* dns_lookup primitive: resolve a hostname to addresses.
 *
 * Name resolution is a precursor to most network activity. getaddrinfo is the
 * standard resolver entry point; resolving "localhost" keeps the primitive
 * offline and deterministic (served from /etc/hosts / nsswitch, no DNS packet)
 * while still exercising the resolver telemetry path.
 *
 * The resolver lives in libc, so this is a strong glibc-vs-musl discriminator:
 * the two implement name resolution differently (NSS modules vs musl's built-in
 * resolver). It is also where Go's cgo/pure-Go split diverges most. Exits 0 when
 * resolution yields at least one address.
 *
 * Linux-only for this pass (getaddrinfo via ws2tcpip on Windows -- issue #44). */
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
