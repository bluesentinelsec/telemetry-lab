// Target rule: Clear Log Activities
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"log_truncate")) return 0;
    truncate_file("/var/log/lab.log");
    printf("CASE_OK log_truncate\n");
    return 0;
}
