#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_word_addin" << "\n";
    if(!fixture_begin(argc,argv,"registry_word_addin")) return 0;
    set_registry_verified("Software\\Microsoft\\Office\\Word\\Addins\\TelemetryLabFixture", "Manifest", "C:\\lab\\windows-coverage\\fixtures\\fixture.vsto");
    success("registry_word_addin"); return 0;
}
