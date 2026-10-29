// Target rule: Netcat Remote Code Execution in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../internal/utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"netcat_exec")) return 0;
const char *args[] = {"/usr/bin/ncat", "--exec", "/usr/bin/printf NETCAT_OK", "198.18.0.1", "4444", NULL};
launch_verified(args, "", 0, NULL, NULL);
verify_bytes("/tmp/lab/received", "NETCAT_OK", 9);
printf("CASE_OK netcat_exec\n");
return 0;
}
