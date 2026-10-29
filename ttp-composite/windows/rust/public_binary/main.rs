// Target rule: Suspicious Binaries and Scripts in Public Folder
// Sigma rule ID: ef4c38c9-e26f-dcfe-1cbe-6323bafb8f39
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_public_folder_extension.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE public_binary\n");
    if !fixture::begin("public_binary") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\helper.exe",
        r"C:\Users\Public\telemetry-lab\fixture.exe",
    );

    fixture::success("public_binary");
}
