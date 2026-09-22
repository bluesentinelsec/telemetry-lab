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
