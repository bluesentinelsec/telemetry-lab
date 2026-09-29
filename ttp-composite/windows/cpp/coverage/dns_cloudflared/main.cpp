#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_cloudflared" << "\n";
    if (!fixture_begin(argc,argv,"dns_cloudflared")) return 0;
    resolve_verified("protocol-v2.argotunnel.com");
    success("dns_cloudflared");
    return 0;
}
