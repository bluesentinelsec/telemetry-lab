fn main() {
    if !coverage_suite::begin("sensitive_read") {
        return;
    }
    coverage_suite::read_file("/etc/shadow");
    println!("CASE_OK sensitive_read");
}
