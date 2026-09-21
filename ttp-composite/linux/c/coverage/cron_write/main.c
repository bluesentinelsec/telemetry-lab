#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"cron_write")) return 0;
    file_write("/etc/cron.d/lab_fixture");
    printf("CASE_OK cron_write\n");
    return 0;
}
