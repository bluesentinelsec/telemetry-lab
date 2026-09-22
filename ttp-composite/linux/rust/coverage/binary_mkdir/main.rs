fn main() {
    if !coverage_suite::begin("binary_mkdir") {
        return;
    }
    coverage_suite::directory("/usr/bin/lab_directory");
    assert!(std::fs::metadata("/usr/bin/lab_directory")
        .unwrap()
        .is_dir());
    std::fs::remove_dir("/usr/bin/lab_directory").unwrap();
    println!("CASE_OK binary_mkdir");
}
