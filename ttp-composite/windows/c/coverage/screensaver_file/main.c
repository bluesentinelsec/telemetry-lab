#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE screensaver_file");
    if(!fixture_begin(argc,argv,"screensaver_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\fixture.scr");
    success("screensaver_file"); return 0;
}
