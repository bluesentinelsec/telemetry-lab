#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE errorhandler_file\n";
    if(!fixture_begin(argc,argv,"errorhandler_file")) return 0;
    copy_verified(ROOT "\\fixtures\\text.txt","C:\\Windows\\Setup\\Scripts\\ErrorHandler.cmd");
    success("errorhandler_file"); return 0;
}
