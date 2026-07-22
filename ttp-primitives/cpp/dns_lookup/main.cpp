// dns_lookup primitive: resolve a hostname to addresses.
//
// Name resolution is a precursor to most network activity. getaddrinfo is the
// standard resolver entry point; resolving "localhost" keeps the primitive
// offline and deterministic (served from /etc/hosts / nsswitch, no DNS packet)
// while still exercising the resolver telemetry path.
//
// The resolver lives in libc, so this is a strong glibc-vs-musl discriminator:
// the two implement name resolution differently (NSS modules vs musl's built-in
// resolver). It is also where Go's cgo/pure-Go split diverges most. Exits 0
// when resolution yields at least one address.
//
// getaddrinfo is raw POSIX and touches no C++ stdlib type, so the
// namespace-scope std::string below anchors libstdc++/libc++ into the binary;
// see empty/main.cpp for the full rationale.
//
// Linux-only for this pass (getaddrinfo via ws2tcpip on Windows -- issue #44).
#include <string>
#include <cstring>
#include <netdb.h>

// Substrate anchor: forces the C++ standard library to be linked. See
// empty/main.cpp for the full rationale.
std::string stdlib_anchor;

int main() {
    struct addrinfo hints;
    struct addrinfo* res = nullptr;
    std::memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo("localhost", "80", &hints, &res) != 0 || res == nullptr) {
        return 1;
    }
    freeaddrinfo(res);
    return 0;
}
