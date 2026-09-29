#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_office_macro");
    if(!fixture_begin(argc,argv,"registry_office_macro")) return 0;
    set_registry_dword_verified("Software\\Microsoft\\Office\\16.0\\Word\\Security", "VBAWarnings", 1);
    success("registry_office_macro"); return 0;
}
