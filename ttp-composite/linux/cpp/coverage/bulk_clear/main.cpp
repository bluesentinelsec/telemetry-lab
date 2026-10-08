#include "../common.hpp"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"bulk_clear")) return 0;
const char *args[] = {"/usr/bin/shred", "-n", "0", "-z", "-s", "64", "/tmp/lab/shred-target", NULL};
launch_verified(args, "", 0, NULL, NULL);
verify_bytes("/tmp/lab/shred-target", "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000", 64);
std::cout << "CASE_OK bulk_clear\n";
return 0;
}
