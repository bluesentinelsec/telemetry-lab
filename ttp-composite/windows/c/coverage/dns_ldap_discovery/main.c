#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_ldap_discovery");
    if (!fixture_begin(argc,argv,"dns_ldap_discovery")) return 0;
    resolve_verified("_ldap.telemetry-lab.test");
    success("dns_ldap_discovery");
    return 0;
}
