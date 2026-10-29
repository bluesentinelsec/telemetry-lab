// Target rule: Potential Persistence Via TypedPaths
// Sigma rule ID: a1229092-bf43-58f9-b9b4-f8fc3da816e6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_typed_paths.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_typed_paths");
    if(!fixture_begin(argc,argv,"registry_typed_paths")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths", "url99", "C:\\lab\\windows-coverage\\work");
    success("registry_typed_paths"); return 0;
}
