// Target rule: Packet socket created in container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"packet_socket")) return 0;
    /* Linux ETH_P_ALL; avoid importing glibc-specific kernel header paths. */
    int fd=socket(AF_PACKET,SOCK_RAW,htons(0x0003)); CHECK(fd >= 0); CHECK(close(fd) == 0);
    std::cout << "CASE_OK packet_socket\n";
    return 0;
}
