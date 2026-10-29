// Target rule: Read ssh information
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"ssh_read")) return 0;
    file_read("/root/.ssh/lab_key");
    printf("CASE_OK ssh_read\n");
    return 0;
}
