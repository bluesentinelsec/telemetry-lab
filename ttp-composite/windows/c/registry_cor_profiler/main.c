// Target rule: Enabling COR Profiler Environment Variables
// Sigma rule ID: aeac22f7-e219-1561-df1f-f531ac2d096f
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_enabling_cor_profiler_env_variables.yml
#include "../internal/common.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_cor_profiler");
    if(!fixture_begin(argc,argv,"registry_cor_profiler")) return 0;
    set_registry_verified("Environment", "COR_PROFILER", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
    success("registry_cor_profiler"); return 0;
}
