// Target rule: Cloudflared Tunnels Related DNS Requests
// Sigma rule ID: a19966bd-8f14-3aaf-c121-4c5d016441d3
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_cloudflared_communication.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_cloudflared\n");
    if !fixture::begin("dns_cloudflared") {
        fixture::hold();
        return;
    }
    fixture::netio::resolve("protocol-v2.argotunnel.com");

    fixture::hold();
    fixture::success("dns_cloudflared");
}
