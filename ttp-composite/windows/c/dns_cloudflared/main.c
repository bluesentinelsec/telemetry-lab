// Target rule: Cloudflared Tunnels Related DNS Requests
// Sigma rule ID: a19966bd-8f14-3aaf-c121-4c5d016441d3
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_cloudflared_communication.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_cloudflared");
    if (!fixture_begin(argc,argv,"dns_cloudflared")) { Sleep(5000); return 0; }
    resolve_verified("protocol-v2.argotunnel.com");
    Sleep(5000); /* Same fixed post-I/O lifetime as TCP, including controls. */
    success("dns_cloudflared");
    return 0;
}
