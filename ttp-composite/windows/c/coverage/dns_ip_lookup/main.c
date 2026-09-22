#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"dns_ip_lookup")) return 0;
    resolve_verified("api.ipify.org");
    success("dns_ip_lookup");
    return 0;
}
