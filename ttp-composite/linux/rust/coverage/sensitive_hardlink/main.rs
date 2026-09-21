fn main() {
    if !coverage_suite::begin("sensitive_hardlink") {
        return;
    }
    use std::os::unix::fs::MetadataExt;
    std::fs::hard_link("/etc/shadow", "/tmp/lab/hard").unwrap();
    let a = std::fs::metadata("/etc/shadow").unwrap();
    let b = std::fs::metadata("/tmp/lab/hard").unwrap();
    assert_eq!((a.dev(), a.ino()), (b.dev(), b.ino()));
    std::fs::remove_file("/tmp/lab/hard").unwrap();
    println!("CASE_OK sensitive_hardlink");
}
