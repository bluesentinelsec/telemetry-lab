// Target rule: Launch Ingress Remote File Copy Tools in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"
#include "../internal/utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"ingress_copy")) return 0;
const char *args[] = {"/usr/bin/curl", "-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture", "-o", "/tmp/lab/downloaded", NULL};
launch_verified(args, "", 0, NULL, NULL);
verify_bytes("/tmp/lab/downloaded", "telemetry-lab-fixture\n", 22);
std::cout << "CASE_OK ingress_copy\n";
return 0;
}
