// Target rule: CurrentVersion Autorun Keys Modification
// Sigma rule ID: 3f59aeed-e4fb-6b21-a7fa-a327fdb8494d
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_asep_reg_keys_modification_currentversion.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE registry_run_key");
    if (!fixture_begin(argc,argv,"registry_run_key")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Run","TelemetryLabCoverage","C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_run_key");
    return 0;
}
