#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE system_name_file");
    if(!fixture_begin(argc,argv,"system_name_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\svchost.exe");
    success("system_name_file"); return 0;
}
