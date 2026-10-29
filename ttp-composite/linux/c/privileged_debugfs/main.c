// Target rule: Debugfs Launched in Privileged Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../internal/utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"privileged_debugfs")) return 0;
const char *args[] = {"/usr/sbin/debugfs", "-R", "cat /marker", "/tmp/lab/filesystem.img", NULL};
launch_verified(args, "telemetry-lab-fixture\n", 0, NULL, NULL);
printf("CASE_OK privileged_debugfs\n");
return 0;
}
