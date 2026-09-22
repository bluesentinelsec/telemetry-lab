fn main() {
    if !coverage_suite::begin("log_truncate") {
        return;
    }
    coverage_suite::truncate_file("/var/log/lab.log");
    println!("CASE_OK log_truncate");
}
