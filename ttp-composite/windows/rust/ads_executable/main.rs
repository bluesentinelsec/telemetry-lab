// Target rule: Hidden Executable In NTFS Alternate Data Stream
// Sigma rule ID: e5cca2eb-74d0-c45b-ec14-3c09f568f8c0
// Ruleset path: sigma/sysmon/create_stream_hash/create_stream_hash_ads_executable.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE ads_executable\n");
    if !fixture::begin("ads_executable") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\helper.exe",
        r"C:\lab\windows-coverage\work\carrier.txt:fixture.exe",
    );

    fixture::success("ads_executable");
}
