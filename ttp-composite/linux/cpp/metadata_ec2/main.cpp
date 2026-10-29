// Target rule: Contact EC2 Instance Metadata Service From Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/network.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"metadata_ec2")) return 0;
    tcp_exchange("169.254.169.254",0);
    std::cout << "CASE_OK metadata_ec2\n";
    return 0;
}
