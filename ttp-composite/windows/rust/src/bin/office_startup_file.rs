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
