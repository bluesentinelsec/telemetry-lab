// Target rule: Suspicious Environment Variable Has Been Registered
// Sigma rule ID: eca534f8-005d-bb79-798d-0af4e2bf38d6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_suspicious_env_variables.yml
#include "../internal/common.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_suspicious_env");
    if(!fixture_begin(argc,argv,"registry_suspicious_env")) return 0;
    set_registry_verified("Environment", "TelemetryLabFixture", "C:\\Users\\Public\\telemetry-lab\\fixture.exe");
    success("registry_suspicious_env"); return 0;
}
