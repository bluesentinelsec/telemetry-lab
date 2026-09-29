#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_word_addin");
    if(!fixture_begin(argc,argv,"registry_word_addin")) return 0;
    set_registry_verified("Software\\Microsoft\\Office\\Word\\Addins\\TelemetryLabFixture", "Manifest", "C:\\lab\\windows-coverage\\fixtures\\fixture.vsto");
    success("registry_word_addin"); return 0;
}
