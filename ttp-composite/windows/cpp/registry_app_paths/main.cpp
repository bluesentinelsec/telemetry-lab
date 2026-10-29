// Target rule: Potential Persistence Via App Paths Default Property
// Sigma rule ID: 140df4ae-d66c-c984-2165-595d754d0424
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_app_paths.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE registry_app_paths" << "\n";
    if (!fixture_begin(argc,argv,"registry_app_paths")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\telemetry-lab-fixture.exe","","C:\\Users\\Public\\telemetry-lab\\helper.exe");
    success("registry_app_paths");
    return 0;
}
