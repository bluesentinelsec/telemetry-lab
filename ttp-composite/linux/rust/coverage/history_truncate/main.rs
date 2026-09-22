fn main() {
    if !coverage_suite::begin("history_truncate") {
        return;
    }
    coverage_suite::truncate_file("/root/.bash_history");
    println!("CASE_OK history_truncate");
}
