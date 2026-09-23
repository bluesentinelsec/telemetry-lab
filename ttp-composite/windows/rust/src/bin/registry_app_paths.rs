use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_app_paths\n");
    if !fixture::begin("registry_app_paths") {
        return;
    }
    fixture::registry::set_verified(
        r"Software\Microsoft\Windows\CurrentVersion\App Paths\telemetry-lab-fixture.exe",
        r"",
        r"C:\Users\Public\telemetry-lab\helper.exe",
    );

    fixture::success("registry_app_paths");
}
