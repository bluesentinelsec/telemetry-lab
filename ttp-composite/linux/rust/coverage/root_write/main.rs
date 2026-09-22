fn main() {
    if !coverage_suite::begin("root_write") {
        return;
    }
    coverage_suite::write_file("/root/lab_fixture");
    println!("CASE_OK root_write");
}
