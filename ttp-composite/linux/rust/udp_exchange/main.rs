// Target rule: Unexpected UDP Traffic
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("udp_exchange") {
        return;
    }
    coverage_suite::udp_exchange();
    println!("CASE_OK udp_exchange");
}
