// Target rule: Path To Screensaver Binary Modified
// Sigma rule ID: ec1e8c56-2fa0-7417-e4b3-517d291e30b2
// Ruleset path: sigma/sysmon/registry/registry_event/registry_event_modify_screensaver_binary_path.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_screensaver\n");
    if !fixture::begin("registry_screensaver") {
        return;
    }
    fixture::registry::set_verified(
        r"Control Panel\Desktop",
        r"SCRNSAVE.EXE",
        r"C:\lab\windows-coverage\fixtures\helper.exe",
    );

    fixture::success("registry_screensaver");
}
