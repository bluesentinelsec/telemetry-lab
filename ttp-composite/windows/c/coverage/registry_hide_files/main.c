#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_hide_files");
    if(!fixture_begin(argc,argv,"registry_hide_files")) return 0;
    set_registry_dword_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden", 0);
    success("registry_hide_files"); return 0;
}
