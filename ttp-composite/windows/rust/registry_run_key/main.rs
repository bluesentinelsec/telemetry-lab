// Target rule: CurrentVersion Autorun Keys Modification
// Sigma rule ID: 3f59aeed-e4fb-6b21-a7fa-a327fdb8494d
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_asep_reg_keys_modification_currentversion.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_run_key\n");
    if !fixture::begin("registry_run_key") {
        return;
    }
    fixture::registry::set_verified(
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        r"TelemetryLabCoverage",
        r"C:\lab\windows-coverage\fixtures\helper.exe",
    );

    fixture::success("registry_run_key");
}
