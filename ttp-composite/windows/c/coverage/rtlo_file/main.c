#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE rtlo_file");
    if(!fixture_begin(argc,argv,"rtlo_file")) return 0;
    copy_verified_w(L"C:\\lab\\windows-coverage\\fixtures\\helper.exe",L"C:\\lab\\windows-coverage\\work\\report\u202efdp.exe");
    success("rtlo_file"); return 0;
}
