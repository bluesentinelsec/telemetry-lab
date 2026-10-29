// Target rule: Launch Remote File Copy Tools in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../internal/utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"remote_copy")) return 0;
const char *args[] = {"/usr/bin/rsync", "--port=1873", "rsync://198.18.0.1/fixture/payload", "/tmp/lab/transferred", NULL};
launch_verified(args, "", 0, NULL, NULL);
verify_bytes("/tmp/lab/transferred", "telemetry-lab-fixture\n", 22);
printf("CASE_OK remote_copy\n");
return 0;
}
