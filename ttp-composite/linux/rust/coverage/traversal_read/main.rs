fn main() {
    if !coverage_suite::begin("traversal_read") {
        return;
    }
    coverage_suite::read_file("/tmp/lab/../../etc/shadow");
    println!("CASE_OK traversal_read");
}
