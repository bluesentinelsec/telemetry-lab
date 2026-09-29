#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_remote_access");
    if (!fixture_begin(argc,argv,"dns_remote_access")) return 0;
    resolve_verified("api.splashtop.com");
    success("dns_remote_access");
    return 0;
}
