// Target rule: DNS Query To Remote Access Software Domain From Non-Browser App
// Sigma rule ID: d064cacb-bfe5-9d2b-7e5d-a8346829a158
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_remote_access_software_domains_non_browsers.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_remote_access");
    if (!fixture_begin(argc,argv,"dns_remote_access")) { Sleep(5000); return 0; }
    resolve_verified("api.splashtop.com");
    Sleep(5000); /* Same fixed post-I/O lifetime as TCP, including controls. */
    success("dns_remote_access");
    return 0;
}
