#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE dns_shortener" << "\n";
    if (!fixture_begin(argc,argv,"dns_shortener")) { Sleep(5000); return 0; }
    resolve_verified("tinyurl.com");
    Sleep(5000); /* Same fixed post-I/O lifetime as TCP, including controls. */
    success("dns_shortener");
    return 0;
}
