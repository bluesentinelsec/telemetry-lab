// Target rule: Office Macros Warning Disabled
// Sigma rule ID: 8b6b4194-cfe8-b585-475f-5997e8015fe0
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_office_vba_warnings_tamper.yml
#include "../internal/common.hpp"
#include "../internal/expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_office_macro" << "\n";
    if(!fixture_begin(argc,argv,"registry_office_macro")) return 0;
    set_registry_dword_verified("Software\\Microsoft\\Office\\16.0\\Word\\Security", "VBAWarnings", 1);
    success("registry_office_macro"); return 0;
}
