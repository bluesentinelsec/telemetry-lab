use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_active_setup\n");
    if !fixture::begin("registry_active_setup") {
        return;
    }
    fixture::registry::set_verified(
        r"Software\Microsoft\Active Setup\Installed Components\{9B9C8026-806D-41E2-992A-909553D7A52A}",
        r"StubPath",
        r"C:\lab\windows-coverage\fixtures\helper.exe",
    );

    fixture::success("registry_active_setup");
}
