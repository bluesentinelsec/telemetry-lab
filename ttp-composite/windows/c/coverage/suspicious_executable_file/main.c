#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE suspicious_executable_file");
    if (!fixture_begin(argc,argv,"suspicious_executable_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\lab.sys.exe");
    success("suspicious_executable_file");
    return 0;
}
