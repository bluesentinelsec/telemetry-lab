#include "../common.h"
#include "../launch_fixture.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"package_manager_query")) return 0;
    const char *args[] = {"/usr/bin/dpkg", "--print-architecture", NULL};
    launch_checked(args, "amd64\n", NULL, NULL);
    printf("CASE_OK package_manager_query\n");
    return 0;
}
