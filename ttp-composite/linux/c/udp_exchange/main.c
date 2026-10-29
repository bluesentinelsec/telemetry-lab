// Target rule: Unexpected UDP Traffic
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/network.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"udp_exchange")) return 0;
    udp_exchange();
    printf("CASE_OK udp_exchange\n");
    return 0;
}
