// Target rule: Write below etc
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"etc_write")) return 0;
    file_write("/etc/lab_fixture");
    printf("CASE_OK etc_write\n");
    return 0;
}
