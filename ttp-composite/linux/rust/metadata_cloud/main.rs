// Target rule: Contact cloud metadata service from container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("metadata_cloud") {
        return;
    }
    coverage_suite::metadata_exchange();
    println!("CASE_OK metadata_cloud");
}
