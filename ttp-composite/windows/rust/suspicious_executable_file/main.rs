// Target rule: Suspicious Executable File Creation
// Sigma rule ID: 9512176f-0e9f-7f30-fa82-d414c1c80248
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_executable_creation.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE suspicious_executable_file\n");
    if !fixture::begin("suspicious_executable_file") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\helper.exe",
        r"C:\lab\windows-coverage\work\lab.sys.exe",
    );

    fixture::success("suspicious_executable_file");
}
