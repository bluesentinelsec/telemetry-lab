fn main() {
    if !coverage_suite::begin("cron_write") {
        return;
    }
    coverage_suite::write_file("/etc/cron.d/lab_fixture");
    println!("CASE_OK cron_write");
}
