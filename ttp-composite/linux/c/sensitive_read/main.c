// Target rule: Read sensitive file untrusted
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"sensitive_read")) return 0;
    file_read("/etc/shadow");
    printf("CASE_OK sensitive_read\n");
    return 0;
}
