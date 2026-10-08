#include "../common.h"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"interactive_recon")) return 0;
const char *args[] = {"/usr/bin/script", "-q", "-e", "-c", "exec /usr/bin/id -u", "/dev/null", NULL};
launch_verified(args, "0\r\n", 0, NULL, NULL);
printf("CASE_OK interactive_recon\n");
return 0;
}
