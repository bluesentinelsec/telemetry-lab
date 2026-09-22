#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE ads_executable");
    if (!fixture_begin(argc,argv,"ads_executable")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\carrier.txt:fixture.exe");
    success("ads_executable");
    return 0;
}
