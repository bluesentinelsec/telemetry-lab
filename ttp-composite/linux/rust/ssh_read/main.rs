// Target rule: Read ssh information
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("ssh_read") {
        return;
    }
    coverage_suite::read_file("/root/.ssh/lab_key");
    println!("CASE_OK ssh_read");
}
