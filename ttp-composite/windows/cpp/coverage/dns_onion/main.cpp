#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_onion" << "\n";
    if (!fixture_begin(argc,argv,"dns_onion")) return 0;
    resolve_verified("lab.onion");
    success("dns_onion");
    return 0;
}
