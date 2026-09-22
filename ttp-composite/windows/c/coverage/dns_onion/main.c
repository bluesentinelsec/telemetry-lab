#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"dns_onion")) return 0;
    resolve_verified("lab.onion");
    success("dns_onion");
    return 0;
}
