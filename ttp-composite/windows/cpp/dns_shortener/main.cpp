// Target rule: DNS Query To Common Malware Hosting and Shortener Services
// Sigma rule ID: 7909c849-d650-4178-8739-9884f75c17fe
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_common_malware_hosting_services.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_shortener" << "\n";
    if (!fixture_begin(argc,argv,"dns_shortener")) { Sleep(5000); return 0; }
    resolve_verified("tinyurl.com");
    Sleep(5000); /* Same fixed post-I/O lifetime as TCP, including controls. */
    success("dns_shortener");
    return 0;
}
