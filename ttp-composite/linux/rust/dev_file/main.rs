// Target rule: Create files below dev
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("dev_file") {
        return;
    }
    coverage_suite::write_file("/dev/lab_fixture");
    println!("CASE_OK dev_file");
}
