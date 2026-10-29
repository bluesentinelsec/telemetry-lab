// Target rule: Network Tool Executed During NPM Package Install
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"
#include "../internal/utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"npm_network_tool")) return 0;
const char *args[] = {"/usr/bin/ncat", "--recv-only", "198.18.0.1", "4445", NULL};
launch_verified(args, "telemetry-lab-fixture\n", 0, NULL, NULL);
std::cout << "CASE_OK npm_network_tool\n";
return 0;
}
