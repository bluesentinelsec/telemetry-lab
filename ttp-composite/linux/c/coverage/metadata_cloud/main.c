#include "../network.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"metadata_cloud")) return 0;
    tcp_exchange("169.254.169.254",0);
    printf("CASE_OK metadata_cloud\n");
    return 0;
}
