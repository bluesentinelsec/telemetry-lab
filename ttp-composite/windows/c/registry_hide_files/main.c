// Target rule: Displaying Hidden Files Feature Disabled
// Sigma rule ID: 96cd46a9-33dc-28dc-273e-83bc1fd8adc9
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_hide_file.yml
#include "../internal/common.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_hide_files");
    if(!fixture_begin(argc,argv,"registry_hide_files")) return 0;
    set_registry_dword_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden", 0);
    success("registry_hide_files"); return 0;
}
