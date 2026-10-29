// Target rule: Basic Interactive Reconnaissance
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"
#include "../internal/utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"interactive_recon")) return 0;
const char *args[] = {"/usr/bin/script", "-q", "-e", "-c", "exec /usr/bin/id -u", "/dev/null", NULL};
launch_verified(args, "0\r\n", 0, NULL, NULL);
std::cout << "CASE_OK interactive_recon\n";
return 0;
}
