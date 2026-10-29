// Target rule: DNS Query To Remote Access Software Domain From Non-Browser App
// Sigma rule ID: d064cacb-bfe5-9d2b-7e5d-a8346829a158
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_remote_access_software_domains_non_browsers.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_remote_access\n");
    if !fixture::begin("dns_remote_access") {
        fixture::hold();
        return;
    }
    fixture::netio::resolve("api.splashtop.com");

    fixture::hold();
    fixture::success("dns_remote_access");
}
