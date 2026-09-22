use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_run_key\n");
    if !fixture::begin("registry_run_key") {
        return;
    }
    fixture::registry::set_verified(
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        r"TelemetryLabCoverage",
        r"C:\lab\windows-coverage\fixtures\helper.exe",
    );

    fixture::success("registry_run_key");
}
