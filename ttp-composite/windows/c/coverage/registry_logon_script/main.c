#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_logon_script");
    if(!fixture_begin(argc,argv,"registry_logon_script")) return 0;
    set_registry_verified("Environment", "UserInitMprLogonScript", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_logon_script"); return 0;
}
