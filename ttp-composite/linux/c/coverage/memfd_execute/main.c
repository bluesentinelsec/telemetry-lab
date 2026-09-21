#include "../process.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"memfd_execute")) return 0;
    execute_helper(NULL,1);
    printf("CASE_OK memfd_execute\n");
    return 0;
}
