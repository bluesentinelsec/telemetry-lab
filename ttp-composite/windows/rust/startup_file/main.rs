// Target rule: Startup Folder File Write
// Sigma rule ID: daaf04a9-5b60-e331-6611-a3a32797e550
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_startup_folder_file_write.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE startup_file\n");
    if !fixture::begin("startup_file") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\text.txt",
        fixture::appdata(
            r"Microsoft\Windows\Start Menu\Programs\Startup\telemetry-lab-fixture.txt",
        ),
    );

    fixture::success("startup_file");
}
