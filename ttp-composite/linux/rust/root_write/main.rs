// Target rule: Write below root
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("root_write") {
        return;
    }
    coverage_suite::write_file("/root/lab_fixture");
    println!("CASE_OK root_write");
}
