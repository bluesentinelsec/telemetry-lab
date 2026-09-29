#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE screensaver_file\n";
    if(!fixture_begin(argc,argv,"screensaver_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\fixture.scr");
    success("screensaver_file"); return 0;
}
