use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE double_extension_execute\n");
    if !fixture::begin("double_extension_execute") {
        return;
    }
    let status = std::process::Command::new(r"C:\lab\windows-coverage\work\report.pdf.exe")
        .status()
        .unwrap();
    assert_eq!(status.code(), Some(42), "helper exit differs");

    fixture::success("double_extension_execute");
}
