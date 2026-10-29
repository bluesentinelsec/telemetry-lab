// Target rule: Suspicious LNK Double Extension File Created
// Sigma rule ID: 6b7cbf57-a67c-6e5a-61c6-4d92d02fff3e
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_lnk_double_extension.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE double_extension_lnk\n");
    if !fixture::begin("double_extension_lnk") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\fixture.lnk",
        r"C:\lab\windows-coverage\work\report.pdf.lnk",
    );

    fixture::success("double_extension_lnk");
}
