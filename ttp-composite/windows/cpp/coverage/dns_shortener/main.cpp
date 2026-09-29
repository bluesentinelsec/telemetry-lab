#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_shortener" << "\n";
    if (!fixture_begin(argc,argv,"dns_shortener")) return 0;
    resolve_verified("tinyurl.com");
    success("dns_shortener");
    return 0;
}
