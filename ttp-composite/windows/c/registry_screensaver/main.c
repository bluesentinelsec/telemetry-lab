// Target rule: Path To Screensaver Binary Modified
// Sigma rule ID: ec1e8c56-2fa0-7417-e4b3-517d291e30b2
// Ruleset path: sigma/sysmon/registry/registry_event/registry_event_modify_screensaver_binary_path.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE registry_screensaver");
    if (!fixture_begin(argc,argv,"registry_screensaver")) return 0;
    set_registry_verified("Control Panel\\Desktop","SCRNSAVE.EXE","C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_screensaver");
    return 0;
}
