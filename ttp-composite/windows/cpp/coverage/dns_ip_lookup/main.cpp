#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_ip_lookup" << "\n";
    if (!fixture_begin(argc,argv,"dns_ip_lookup")) { Sleep(5000); return 0; }
    resolve_verified("api.ipify.org");
    Sleep(5000); /* Same fixed post-I/O lifetime as TCP, including controls. */
    success("dns_ip_lookup");
    return 0;
}
