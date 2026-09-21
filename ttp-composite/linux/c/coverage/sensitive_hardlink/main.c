#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"sensitive_hardlink")) return 0;
    CHECK(link("/etc/shadow","/tmp/lab/hard") == 0);
    struct stat a,b; CHECK(stat("/etc/shadow",&a) == 0 && stat("/tmp/lab/hard",&b) == 0);
    CHECK(a.st_dev == b.st_dev && a.st_ino == b.st_ino); CHECK(unlink("/tmp/lab/hard") == 0);
    printf("CASE_OK sensitive_hardlink\n");
    return 0;
}
