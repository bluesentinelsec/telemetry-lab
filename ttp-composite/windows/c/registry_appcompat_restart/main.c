// Target rule: Potential Persistence Via AppCompat RegisterAppRestart Layer
// Sigma rule ID: 349ed81d-2f2f-a95f-2d5d-41e5fbeaf784
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_app_cpmpat_layer_registerapprestart.yml
#include "../internal/common.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_appcompat_restart");
    if(!fixture_begin(argc,argv,"registry_appcompat_restart")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers", "C:\\lab\\windows-coverage\\fixtures\\helper.exe", "REGISTERAPPRESTART");
    success("registry_appcompat_restart"); return 0;
}
