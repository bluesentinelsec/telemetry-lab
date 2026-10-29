// Target rule: Directory traversal monitored file read
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"traversal_read")) return 0;
    file_read("/tmp/lab/../../etc/shadow");
    printf("CASE_OK traversal_read\n");
    return 0;
}
