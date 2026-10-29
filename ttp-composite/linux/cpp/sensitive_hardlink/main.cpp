// Target rule: Create Hardlink Over Sensitive Files
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"sensitive_hardlink")) return 0;
    fs::create_hard_link("/etc/shadow", "/tmp/lab/hard");
    CHECK(fs::equivalent("/etc/shadow", "/tmp/lab/hard"));
    CHECK(fs::remove("/tmp/lab/hard"));
    std::cout << "CASE_OK sensitive_hardlink\n";
    return 0;
}
