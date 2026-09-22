fn main() {
    if !coverage_suite::begin("ssh_read") {
        return;
    }
    coverage_suite::read_file("/root/.ssh/lab_key");
    println!("CASE_OK ssh_read");
}
