// Target rule: Delete or rename shell history
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("history_truncate") {
        return;
    }
    coverage_suite::truncate_file("/root/.bash_history");
    println!("CASE_OK history_truncate");
}
