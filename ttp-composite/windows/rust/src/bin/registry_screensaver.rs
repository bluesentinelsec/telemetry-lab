use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_screensaver\n");
    if !fixture::begin("registry_screensaver") {
        return;
    }
    fixture::registry::set_verified(
        r"Control Panel\Desktop",
        r"SCRNSAVE.EXE",
        r"C:\lab\windows-coverage\fixtures\helper.exe",
    );

    fixture::success("registry_screensaver");
}
