#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"packet_socket")) return 0;
    /* Linux ETH_P_ALL; avoid importing glibc-specific kernel header paths. */
    int fd=socket(AF_PACKET,SOCK_RAW,htons(0x0003)); CHECK(fd >= 0); CHECK(close(fd) == 0);
    printf("CASE_OK packet_socket\n");
    return 0;
}
