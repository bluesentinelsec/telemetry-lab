// Target rule: Mkdir binary dirs
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"binary_mkdir")) return 0;
    CHECK(fs::create_directory("/usr/bin/lab_directory"));
    CHECK(fs::is_directory("/usr/bin/lab_directory"));
    CHECK(fs::remove("/usr/bin/lab_directory"));
    std::cout << "CASE_OK binary_mkdir\n";
    return 0;
}
