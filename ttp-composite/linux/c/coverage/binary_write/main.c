#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"binary_write")) return 0;
    file_write("/usr/bin/lab_fixture");
    printf("CASE_OK binary_write\n");
    return 0;
}
