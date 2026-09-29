#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE errorhandler_file");
    if(!fixture_begin(argc,argv,"errorhandler_file")) return 0;
    copy_verified(ROOT "\\fixtures\\text.txt","C:\\Windows\\Setup\\Scripts\\ErrorHandler.cmd");
    success("errorhandler_file"); return 0;
}
