#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_hide_files" << "\n";
    if(!fixture_begin(argc,argv,"registry_hide_files")) return 0;
    set_registry_dword_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden", 0);
    success("registry_hide_files"); return 0;
}
