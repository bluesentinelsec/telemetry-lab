// Target rule: Suspicious DNS Query for IP Lookup Service APIs
// Sigma rule ID: e1d5e512-66be-e3eb-e24b-a9f3545e115a
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_susp_external_ip_lookup.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_ip_lookup\n");
    if !fixture::begin("dns_ip_lookup") {
        fixture::hold();
        return;
    }
    fixture::netio::resolve("api.ipify.org");

    fixture::hold();
    fixture::success("dns_ip_lookup");
}
