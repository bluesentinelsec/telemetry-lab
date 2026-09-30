#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_cloudflared");
    if (!fixture_begin(argc,argv,"dns_cloudflared")) { Sleep(5000); return 0; }
    resolve_verified("protocol-v2.argotunnel.com");
    Sleep(5000); /* Same fixed post-I/O lifetime as TCP, including controls. */
    success("dns_cloudflared");
    return 0;
}
