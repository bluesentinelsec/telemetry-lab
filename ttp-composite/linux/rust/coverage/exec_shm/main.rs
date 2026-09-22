fn main() {
    if !coverage_suite::begin("exec_shm") {
        return;
    }
    coverage_suite::execute_helper("/dev/shm/lab-helper", false);
    println!("CASE_OK exec_shm");
}
