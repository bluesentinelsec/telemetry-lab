// Target rule: Potential Persistence Via App Paths Default Property
// Sigma rule ID: 140df4ae-d66c-c984-2165-595d754d0424
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_app_paths.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_app_paths\n");
    if !fixture::begin("registry_app_paths") {
        return;
    }
    fixture::registry::set_verified(
        r"Software\Microsoft\Windows\CurrentVersion\App Paths\telemetry-lab-fixture.exe",
        r"",
        r"C:\Users\Public\telemetry-lab\helper.exe",
    );

    fixture::success("registry_app_paths");
}
