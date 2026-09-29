#include "../common.hpp"
#include "../launch_fixture.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"glibc_tunable_child")) return 0;
    const char *args[] = {"/opt/coverage/helper", NULL};
    launch_checked(args, "HELPER_OK\n", "GLIBC_TUNABLES", "glibc.malloc.trim_threshold=131072");
    std::cout << "CASE_OK glibc_tunable_child\n";
    return 0;
}
