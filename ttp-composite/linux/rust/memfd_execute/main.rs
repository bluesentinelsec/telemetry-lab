// Target rule: Fileless execution via memfd_create
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("memfd_execute") {
        return;
    }
    coverage_suite::execute_helper("", true);
    println!("CASE_OK memfd_execute");
}
