// Target rule: Kubernetes Client Tool Launched in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../internal/utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"k8s_client")) return 0;
const char *args[] = {"/usr/bin/docker", "--version", NULL};
launch_verified(args, "Docker version ", 1, NULL, NULL);
printf("CASE_OK k8s_client\n");
return 0;
}
