// dns_lookup primitive: resolve a hostname to addresses.
//
// Name resolution is a precursor to most network activity. getaddrinfo is the
// standard resolver entry point; resolving "localhost" keeps the primitive
// offline and deterministic (served from the hosts file, no DNS packet) while
// still exercising the resolver telemetry path.
//
// On POSIX the resolver lives in libc, so this is a strong glibc-vs-musl
// discriminator (NSS modules vs musl's built-in resolver) and where Go's
// cgo/pure-Go split diverges most. On Windows getaddrinfo is provided by
// Winsock (linking ws2_32). Exits 0 when resolution yields at least one address.
//
// getaddrinfo is raw platform API touching no C++ stdlib type, so the
// namespace-scope std::string below anchors libstdc++/libc++ into the binary;
// see empty/main.cpp for the full rationale.
#include <cstring>
#include <string>
#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <netdb.h>
#endif

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

int main() {
#ifdef _WIN32
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        return 1;
    }
#endif
    struct addrinfo hints;
    struct addrinfo* res = nullptr;
    std::memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    int rc = getaddrinfo("localhost", "80", &hints, &res);
    if (rc == 0 && res != nullptr) {
        freeaddrinfo(res);
    }
#ifdef _WIN32
    WSACleanup();
#endif
    return (rc == 0 && res != nullptr) ? 0 : 1;
}
