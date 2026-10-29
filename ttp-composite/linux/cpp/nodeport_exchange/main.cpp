// Target rule: Unexpected K8s NodePort Connection
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"
#include "../internal/utility.h"
int main(int argc,char **argv) {if (!fixture_begin(argc,argv,"nodeport_exchange")) return 0;
port_exchange(30080);
std::cout << "CASE_OK nodeport_exchange\n";
}
