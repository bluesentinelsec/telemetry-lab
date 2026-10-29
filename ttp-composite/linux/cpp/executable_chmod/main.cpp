// Target rule: Container Drift Detected (chmod)
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"
#include "../internal/utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"executable_chmod")) return 0;
fs::permissions("/tmp/lab/executable-mode",fs::perms::owner_all,fs::perm_options::replace); CHECK((fs::status("/tmp/lab/executable-mode").permissions() & fs::perms::mask)==fs::perms::owner_all);
std::cout << "CASE_OK executable_chmod\n";
}
