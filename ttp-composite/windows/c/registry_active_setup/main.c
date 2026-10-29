// Target rule: Run Once Task Configuration in Registry
// Sigma rule ID: 46f90542-f6e6-75d1-c29d-e26535273ec0
// Ruleset path: sigma/sysmon/registry/registry_event/registry_event_runonce_persistence.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE registry_active_setup");
    if (!fixture_begin(argc,argv,"registry_active_setup")) return 0;
    set_registry_verified("Software\\Microsoft\\Active Setup\\Installed Components\\{9B9C8026-806D-41E2-992A-909553D7A52A}","StubPath","C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_active_setup");
    return 0;
}
