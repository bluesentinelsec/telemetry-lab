// Target rule: Write below binary dir
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("binary_write") {
        return;
    }
    coverage_suite::write_file("/usr/bin/lab_fixture");
    println!("CASE_OK binary_write");
}
