// Target rule: Write below monitored dir
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("monitored_write") {
        return;
    }
    coverage_suite::write_file("/boot/lab_fixture");
    println!("CASE_OK monitored_write");
}
