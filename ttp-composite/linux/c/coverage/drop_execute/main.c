#include "../process.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"drop_execute")) return 0;
    execute_helper("/tmp/lab-helper",0);
    printf("CASE_OK drop_execute\n");
    return 0;
}
