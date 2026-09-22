#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_onion");
    if (!fixture_begin(argc,argv,"dns_onion")) return 0;
    resolve_verified("lab.onion");
    success("dns_onion");
    return 0;
}
