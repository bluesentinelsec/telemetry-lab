use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE suspicious_executable_file\n");
    if !fixture::begin("suspicious_executable_file") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\helper.exe",
        r"C:\lab\windows-coverage\work\lab.sys.exe",
    );

    fixture::success("suspicious_executable_file");
}
