// Target rule: Adding ssh keys to authorized_keys
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"authorized_keys")) return 0;
    file_write("/root/.ssh/authorized_keys");
    printf("CASE_OK authorized_keys\n");
    return 0;
}
