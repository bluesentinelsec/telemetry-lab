fn main() {
    if !coverage_suite::begin("binary_write") {
        return;
    }
    coverage_suite::write_file("/usr/bin/lab_fixture");
    println!("CASE_OK binary_write");
}
