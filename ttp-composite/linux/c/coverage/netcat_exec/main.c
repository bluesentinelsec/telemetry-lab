#include "../common.h"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"netcat_exec")) return 0;
const char *args[] = {"/usr/bin/ncat", "--exec", "/usr/bin/printf NETCAT_OK", "198.18.0.1", "4444", NULL};
launch_verified(args, "", 0, NULL, NULL);
verify_bytes("/tmp/lab/received", "NETCAT_OK", 9);
printf("CASE_OK netcat_exec\n");
return 0;
}
