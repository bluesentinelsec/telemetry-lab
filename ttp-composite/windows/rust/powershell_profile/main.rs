// Target rule: PowerShell Profile Modification
// Sigma rule ID: 5d1e6a6b-91ca-c7e8-821c-5c665ad9ca5e
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_powershell_profile.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE powershell_profile\n");
    if !fixture::begin("powershell_profile") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\profile.ps1",
        fixture::appdata(r"Microsoft\Windows\PowerShell\Microsoft.PowerShell_profile.ps1"),
    );

    fixture::success("powershell_profile");
}
