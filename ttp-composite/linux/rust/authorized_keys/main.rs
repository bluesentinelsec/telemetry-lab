// Target rule: Adding ssh keys to authorized_keys
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("authorized_keys") {
        return;
    }
    coverage_suite::write_file("/root/.ssh/authorized_keys");
    println!("CASE_OK authorized_keys");
}
