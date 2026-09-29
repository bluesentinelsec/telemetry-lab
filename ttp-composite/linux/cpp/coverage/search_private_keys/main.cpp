#include "../common.hpp"
#include "../launch_fixture.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"search_private_keys")) return 0;
    const char *args[] = {"/usr/bin/grep", "BEGIN PRIVATE", "/tmp/lab/key-search", NULL};
    launch_checked(args, "BEGIN PRIVATE KEY telemetry-lab\n", NULL, NULL);
    std::cout << "CASE_OK search_private_keys\n";
    return 0;
}
