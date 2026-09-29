#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_appcompat_restart");
    if(!fixture_begin(argc,argv,"registry_appcompat_restart")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers", "C:\\lab\\windows-coverage\\fixtures\\helper.exe", "REGISTERAPPRESTART");
    success("registry_appcompat_restart"); return 0;
}
