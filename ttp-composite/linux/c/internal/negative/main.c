#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"negative")) return 0;
    
    printf("CASE_OK negative\n");
    return 0;
}
