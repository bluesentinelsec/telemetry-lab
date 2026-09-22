use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE double_extension_file\n");
    if !fixture::begin("double_extension_file") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\helper.exe",
        r"C:\lab\windows-coverage\work\report.pdf.exe",
    );

    fixture::success("double_extension_file");
}
