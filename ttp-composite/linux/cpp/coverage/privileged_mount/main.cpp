#include "../common.hpp"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"privileged_mount")) return 0;
const char *args[] = {"/usr/bin/mount", "--bind", "/tmp/lab/mount-source", "/tmp/lab/mount-target", NULL};
launch_verified(args, "", 0, NULL, NULL);
verify_bytes("/tmp/lab/mount-target/payload", "telemetry-lab-fixture\n", 22);
std::cout << "CASE_OK privileged_mount\n";
return 0;
}
