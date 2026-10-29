// Target rule: Fileless execution via memfd_create
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/process.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"memfd_execute")) return 0;
    execute_helper(NULL,1);
    std::cout << "CASE_OK memfd_execute\n";
    return 0;
}
