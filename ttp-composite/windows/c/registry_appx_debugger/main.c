// Target rule: Potential Persistence Using DebugPath
// Sigma rule ID: 1fa31aa7-117f-4356-a2ab-7062be19c8a6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_appx_debugger.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_appx_debugger");
    if(!fixture_begin(argc,argv,"registry_appx_debugger")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\PackagedAppXDebug\\Microsoft.TelemetryLabFixture", "", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_appx_debugger"); return 0;
}
