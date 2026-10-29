// Target rule: Uncommon Connection to Active Directory Web Services
// Sigma rule ID: ae8c1c58-4743-c0c8-3b30-7d69f7cbee68
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_adws_unusual_connection.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE tcp_connect_9389\n");
    if !fixture::begin("tcp_connect_9389") {
        fixture::hold();
        return;
    }
    fixture::netio::exchange(9389);
    fixture::hold();
    fixture::success("tcp_connect_9389");
}
