#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE double_extension_file");
    if (!fixture_begin(argc,argv,"double_extension_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\report.pdf.exe");
    success("double_extension_file");
    return 0;
}
