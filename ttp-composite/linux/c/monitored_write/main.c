// Target rule: Write below monitored dir
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"monitored_write")) return 0;
    file_write("/boot/lab_fixture");
    printf("CASE_OK monitored_write\n");
    return 0;
}
