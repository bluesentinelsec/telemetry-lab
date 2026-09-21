#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"dev_file")) return 0;
    file_write("/dev/lab_fixture");
    printf("CASE_OK dev_file\n");
    return 0;
}
