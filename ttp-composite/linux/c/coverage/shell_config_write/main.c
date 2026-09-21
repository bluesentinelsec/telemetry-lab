#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"shell_config_write")) return 0;
    file_write("/root/.bashrc");
    printf("CASE_OK shell_config_write\n");
    return 0;
}
