// Target rule: Delete or rename shell history
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"history_truncate")) return 0;
    truncate_file("/root/.bash_history");
    printf("CASE_OK history_truncate\n");
    return 0;
}
