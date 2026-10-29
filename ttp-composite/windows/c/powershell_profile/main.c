// Target rule: PowerShell Profile Modification
// Sigma rule ID: 5d1e6a6b-91ca-c7e8-821c-5c665ad9ca5e
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_powershell_profile.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE powershell_profile");
    if (!fixture_begin(argc,argv,"powershell_profile")) return 0;
    char path[MAX_PATH]; appdata_path(path,sizeof path,"Microsoft\\Windows\\PowerShell\\Microsoft.PowerShell_profile.ps1");
    copy_verified(ROOT "\\fixtures\\profile.ps1",path);
    success("powershell_profile");
    return 0;
}
