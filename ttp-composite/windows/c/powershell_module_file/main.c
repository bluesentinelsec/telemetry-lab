// Target rule: PowerShell Module File Created By Non-PowerShell Process
// Sigma rule ID: 103362bb-15b7-3bed-7f8c-fd7a15fe31f4
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_powershell_module_uncommon_creation.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE powershell_module_file");
    if(!fixture_begin(argc,argv,"powershell_module_file")) return 0;
    char path[MAX_PATH]; const char *profile=getenv("USERPROFILE");CHECK(profile && *profile);
    int n=snprintf(path,sizeof path,"%s\\%s",profile,"Documents\\WindowsPowerShell\\Modules\\TelemetryLabFixture\\TelemetryLabFixture.psm1"); CHECK(n>0 && (size_t)n<sizeof path);
    copy_verified(ROOT "\\fixtures\\text.txt",path);
    success("powershell_module_file"); return 0;
}
