#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE dns_remote_access");
    if (!fixture_begin(argc,argv,"dns_remote_access")) { Sleep(5000); return 0; }
    resolve_verified("api.splashtop.com");
    Sleep(5000); /* Same fixed post-I/O lifetime as TCP, including controls. */
    success("dns_remote_access");
    return 0;
}
