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
