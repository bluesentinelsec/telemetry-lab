// Target rule: Suspicious Outbound SMTP Connections
// Sigma rule ID: f8a59cdc-b3d1-8f59-c3f4-4db6d94e8efc
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_outbound_smtp_connections.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE tcp_connect_2525\n");
    if !fixture::begin("tcp_connect_2525") {
        fixture::hold();
        return;
    }
    fixture::netio::exchange(2525);
    fixture::hold();
    fixture::success("tcp_connect_2525");
}
