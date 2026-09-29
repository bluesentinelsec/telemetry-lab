#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE system_name_file\n";
    if(!fixture_begin(argc,argv,"system_name_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\svchost.exe");
    success("system_name_file"); return 0;
}
