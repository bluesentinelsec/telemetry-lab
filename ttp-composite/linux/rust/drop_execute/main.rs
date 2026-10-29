// Target rule: Drop and execute new binary in container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("drop_execute") {
        return;
    }
    coverage_suite::execute_helper("/tmp/lab-helper", false);
    println!("CASE_OK drop_execute");
}
