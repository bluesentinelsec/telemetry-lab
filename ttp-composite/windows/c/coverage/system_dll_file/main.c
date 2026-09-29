#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE system_dll_file");
    if(!fixture_begin(argc,argv,"system_dll_file")) return 0;
    copy_verified(ROOT "\\fixtures\\fixture.node","C:\\lab\\windows-coverage\\work\\secur32.dll");
    success("system_dll_file"); return 0;
}
