// Target rule: Modify binary dirs
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("binary_rename") {
        return;
    }
    std::fs::rename("/usr/bin/lab_old", "/usr/bin/lab_new").unwrap();
    assert!(!std::path::Path::new("/usr/bin/lab_old").exists());
    coverage_suite::read_file("/usr/bin/lab_new");
    println!("CASE_OK binary_rename");
}
