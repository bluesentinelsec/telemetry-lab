// Target rule: DNS Query To Common Malware Hosting and Shortener Services
// Sigma rule ID: 7909c849-d650-4178-8739-9884f75c17fe
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_common_malware_hosting_services.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_shortener\n");
    if !fixture::begin("dns_shortener") {
        fixture::hold();
        return;
    }
    fixture::netio::resolve("tinyurl.com");

    fixture::hold();
    fixture::success("dns_shortener");
}
