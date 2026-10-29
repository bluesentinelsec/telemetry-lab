// Target rule: Write below etc
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("etc_write") {
        return;
    }
    coverage_suite::write_file("/etc/lab_fixture");
    println!("CASE_OK etc_write");
}
