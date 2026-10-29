// Target rule: Suspicious Double Extension File Execution
// Sigma rule ID: b6ce0b2f-593b-5e1c-e137-d30b2974e30e
// Ruleset path: sigma/sysmon/process_creation/proc_creation_win_susp_double_extension.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE double_extension_execute\n");
    if !fixture::begin("double_extension_execute") {
        return;
    }
    let status = std::process::Command::new(r"C:\lab\windows-coverage\work\report.pdf.exe")
        .status()
        .unwrap();
    assert_eq!(status.code(), Some(42), "helper exit differs");

    fixture::success("double_extension_execute");
}
