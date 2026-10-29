// Target rule: Fileless execution via memfd_create
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/process.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"memfd_execute")) return 0;
    execute_helper(NULL,1);
    printf("CASE_OK memfd_execute\n");
    return 0;
}
