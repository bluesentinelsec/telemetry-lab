#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_appcompat_restart" << "\n";
    if(!fixture_begin(argc,argv,"registry_appcompat_restart")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers", "C:\\lab\\windows-coverage\\fixtures\\helper.exe", "REGISTERAPPRESTART");
    success("registry_appcompat_restart"); return 0;
}
