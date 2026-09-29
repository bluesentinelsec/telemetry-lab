#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_shortener");
    if (!fixture_begin(argc,argv,"dns_shortener")) return 0;
    resolve_verified("tinyurl.com");
    success("dns_shortener");
    return 0;
}
