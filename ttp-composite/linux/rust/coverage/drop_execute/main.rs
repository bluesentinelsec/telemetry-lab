fn main() {
    if !coverage_suite::begin("drop_execute") {
        return;
    }
    coverage_suite::execute_helper("/tmp/lab-helper", false);
    println!("CASE_OK drop_execute");
}
