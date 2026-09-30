#include "../common.hpp"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"privileged_debugfs")) return 0;
const char *args[] = {"/usr/sbin/debugfs", "-R", "cat /marker", "/tmp/lab/filesystem.img", NULL};
launch_verified(args, "telemetry-lab-fixture\n", 0, NULL, NULL);
std::cout << "CASE_OK privileged_debugfs\n";
return 0;
}
