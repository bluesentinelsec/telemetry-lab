#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_suspicious_env");
    if(!fixture_begin(argc,argv,"registry_suspicious_env")) return 0;
    set_registry_verified("Environment", "TelemetryLabFixture", "C:\\Users\\Public\\telemetry-lab\\fixture.exe");
    success("registry_suspicious_env"); return 0;
}
