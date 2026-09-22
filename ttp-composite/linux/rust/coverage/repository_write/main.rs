fn main() {
    if !coverage_suite::begin("repository_write") {
        return;
    }
    coverage_suite::write_file("/etc/apt/sources.list.d/lab.list");
    println!("CASE_OK repository_write");
}
