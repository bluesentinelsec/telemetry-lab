#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE system_dll_file\n";
    if(!fixture_begin(argc,argv,"system_dll_file")) return 0;
    copy_verified(ROOT "\\fixtures\\fixture.node","C:\\lab\\windows-coverage\\work\\secur32.dll");
    success("system_dll_file"); return 0;
}
