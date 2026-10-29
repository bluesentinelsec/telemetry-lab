// Target rule: Contact EC2 Instance Metadata Service From Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("metadata_ec2") {
        return;
    }
    coverage_suite::metadata_exchange();
    println!("CASE_OK metadata_ec2");
}
