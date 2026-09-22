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
