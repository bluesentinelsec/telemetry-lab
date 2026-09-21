#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"root_write")) return 0;
    file_write("/root/lab_fixture");
    printf("CASE_OK root_write\n");
    return 0;
}
