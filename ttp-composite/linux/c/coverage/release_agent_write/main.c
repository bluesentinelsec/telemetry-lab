#include "../file_io.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"release_agent_write")) return 0;
    file_write("/tmp/lab/release_agent");
    printf("CASE_OK release_agent_write\n");
    return 0;
}
