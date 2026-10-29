// Target rule: Write below rpm database
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/file_io.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"rpm_database_write")) return 0;
    file_write("/var/lib/rpm/telemetry-lab-fixture");
    printf("CASE_OK rpm_database_write\n");
    return 0;
}
