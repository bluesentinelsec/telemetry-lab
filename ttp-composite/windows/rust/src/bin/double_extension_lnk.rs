use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE double_extension_lnk\n");
    if !fixture::begin("double_extension_lnk") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\fixture.lnk",
        r"C:\lab\windows-coverage\work\report.pdf.lnk",
    );

    fixture::success("double_extension_lnk");
}
