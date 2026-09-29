#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_cloudflared");
    if (!fixture_begin(argc,argv,"dns_cloudflared")) return 0;
    resolve_verified("protocol-v2.argotunnel.com");
    success("dns_cloudflared");
    return 0;
}
