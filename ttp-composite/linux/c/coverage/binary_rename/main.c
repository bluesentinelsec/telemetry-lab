#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"binary_rename")) return 0;
    CHECK(rename("/usr/bin/lab_old","/usr/bin/lab_new") == 0);
    CHECK(access("/usr/bin/lab_old",F_OK) == -1 && errno == ENOENT); file_read("/usr/bin/lab_new");
    printf("CASE_OK binary_rename\n");
    return 0;
}
