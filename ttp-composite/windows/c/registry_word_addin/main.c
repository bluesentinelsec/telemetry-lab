// Target rule: Potential Persistence Via Visual Studio Tools for Office
// Sigma rule ID: ee69bf67-79f6-5973-f69d-7a6f609c97db
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_office_vsto.yml
#include "../internal/common.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_word_addin");
    if(!fixture_begin(argc,argv,"registry_word_addin")) return 0;
    set_registry_verified("Software\\Microsoft\\Office\\Word\\Addins\\TelemetryLabFixture", "Manifest", "C:\\lab\\windows-coverage\\fixtures\\fixture.vsto");
    success("registry_word_addin"); return 0;
}
