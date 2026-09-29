#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE rtlo_file\n";
    if(!fixture_begin(argc,argv,"rtlo_file")) return 0;
    copy_verified_w(L"C:\\lab\\windows-coverage\\fixtures\\helper.exe",L"C:\\lab\\windows-coverage\\work\\report\u202efdp.exe");
    success("rtlo_file"); return 0;
}
