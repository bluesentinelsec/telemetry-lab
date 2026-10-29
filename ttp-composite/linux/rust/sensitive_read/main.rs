// Target rule: Read sensitive file untrusted
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("sensitive_read") {
        return;
    }
    coverage_suite::read_file("/etc/shadow");
    println!("CASE_OK sensitive_read");
}
