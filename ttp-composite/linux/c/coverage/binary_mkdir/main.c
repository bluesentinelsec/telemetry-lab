#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"binary_mkdir")) return 0;
    CHECK(mkdir("/usr/bin/lab_directory",0700) == 0);
    struct stat st; CHECK(stat("/usr/bin/lab_directory",&st) == 0 && S_ISDIR(st.st_mode));
    CHECK(rmdir("/usr/bin/lab_directory") == 0);
    printf("CASE_OK binary_mkdir\n");
    return 0;
}
