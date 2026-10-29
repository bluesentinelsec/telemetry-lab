// Target rule: Potential Persistence Via Logon Scripts - Registry
// Sigma rule ID: aadaadd9-d82e-918a-20ca-01a4f35cde1f
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_logon_scripts_userinitmprlogonscript.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_logon_script");
    if(!fixture_begin(argc,argv,"registry_logon_script")) return 0;
    set_registry_verified("Environment", "UserInitMprLogonScript", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_logon_script"); return 0;
}
