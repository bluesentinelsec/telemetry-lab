#include "../common.h"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"k8s_client")) return 0;
const char *args[] = {"/usr/bin/docker", "--version", NULL};
launch_verified(args, "Docker version ", 1, NULL, NULL);
printf("CASE_OK k8s_client\n");
return 0;
}
