#include "../network.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"udp_exchange")) return 0;
    udp_exchange();
    printf("CASE_OK udp_exchange\n");
    return 0;
}
