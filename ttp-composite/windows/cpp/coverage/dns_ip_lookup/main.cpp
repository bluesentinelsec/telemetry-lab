#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_ip_lookup" << "\n";
    if (!fixture_begin(argc,argv,"dns_ip_lookup")) return 0;
    resolve_verified("api.ipify.org");
    success("dns_ip_lookup");
    return 0;
}
