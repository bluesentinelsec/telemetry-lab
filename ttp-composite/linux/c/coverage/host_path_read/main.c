#include "../file_io.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"host_path_read")) return 0;
    file_read("/host/telemetry-lab/fixture");
    printf("CASE_OK host_path_read\n");
    return 0;
}
