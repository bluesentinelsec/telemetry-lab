fn main() {
    if !coverage_suite::begin("memfd_execute") {
        return;
    }
    coverage_suite::execute_helper("", true);
    println!("CASE_OK memfd_execute");
}
