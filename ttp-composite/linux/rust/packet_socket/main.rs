// Target rule: Packet socket created in container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("packet_socket") {
        return;
    }
    coverage_suite::packet_socket();
    println!("CASE_OK packet_socket");
}
