#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_ldap_discovery" << "\n";
    if (!fixture_begin(argc,argv,"dns_ldap_discovery")) return 0;
    resolve_verified("_ldap.telemetry-lab.test");
    success("dns_ldap_discovery");
    return 0;
}
