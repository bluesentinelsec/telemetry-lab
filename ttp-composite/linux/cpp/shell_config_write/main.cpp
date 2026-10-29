// Target rule: Modify Shell Configuration File
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"shell_config_write")) return 0;
    file_write("/root/.bashrc");
    std::cout << "CASE_OK shell_config_write\n";
    return 0;
}
