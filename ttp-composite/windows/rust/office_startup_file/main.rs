// Target rule: Potential Persistence Via Microsoft Office Startup Folder
// Sigma rule ID: be512a1b-170e-acff-f35d-0e4b44caa2a3
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_office_startup_persistence.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE office_startup_file\n");
    if !fixture::begin("office_startup_file") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\document.rtf",
        fixture::appdata(r"Microsoft\Word\STARTUP\telemetry-lab-fixture.rtf"),
    );

    fixture::success("office_startup_file");
}
