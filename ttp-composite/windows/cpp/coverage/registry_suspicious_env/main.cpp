#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_suspicious_env\n";
    if(!fixture_begin(argc,argv,"registry_suspicious_env")) return 0;
    set_registry_verified("Environment", "TelemetryLabFixture", "C:\\Users\\Public\\telemetry-lab\\fixture.exe");
    success("registry_suspicious_env"); return 0;
}
