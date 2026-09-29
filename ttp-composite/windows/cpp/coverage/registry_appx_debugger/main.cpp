#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_appx_debugger" << "\n";
    if(!fixture_begin(argc,argv,"registry_appx_debugger")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\PackagedAppXDebug\\Microsoft.TelemetryLabFixture", "", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_appx_debugger"); return 0;
}
