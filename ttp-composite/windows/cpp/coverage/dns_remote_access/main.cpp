#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_remote_access" << "\n";
    if (!fixture_begin(argc,argv,"dns_remote_access")) return 0;
    resolve_verified("api.splashtop.com");
    success("dns_remote_access");
    return 0;
}
