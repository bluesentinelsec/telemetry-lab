#include "../common.h"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"proxy_environment")) return 0;
const char *args[] = {"/usr/bin/curl", "-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture", NULL};
launch_verified(args, "telemetry-lab-fixture\n", 0, "HTTP_PROXY", "http://198.18.0.1:18081");
printf("CASE_OK proxy_environment\n");
return 0;
}
