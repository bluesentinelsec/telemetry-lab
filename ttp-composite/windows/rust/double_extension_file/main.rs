// Target rule: Suspicious Double Extension Files
// Sigma rule ID: c69c8c8d-4188-72ea-ca61-a2a1a80612b3
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_double_extension.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE double_extension_file\n");
    if !fixture::begin("double_extension_file") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\helper.exe",
        r"C:\lab\windows-coverage\work\report.pdf.exe",
    );

    fixture::success("double_extension_file");
}
