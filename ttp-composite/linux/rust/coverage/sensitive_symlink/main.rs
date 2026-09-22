fn main() {
    if !coverage_suite::begin("sensitive_symlink") {
        return;
    }
    std::os::unix::fs::symlink("/etc/shadow", "/tmp/lab/link").unwrap();
    assert_eq!(
        std::fs::read_link("/tmp/lab/link").unwrap(),
        std::path::Path::new("/etc/shadow")
    );
    std::fs::remove_file("/tmp/lab/link").unwrap();
    println!("CASE_OK sensitive_symlink");
}
