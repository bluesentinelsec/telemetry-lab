// Target rule: Uncommon Outbound Kerberos Connection
// Sigma rule ID: 322fd5f2-b5b7-1bf4-58f2-92873dc878bb
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_outbound_kerberos_connection.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE tcp_connect_88\n");
    if !fixture::begin("tcp_connect_88") {
        fixture::hold();
        return;
    }
    fixture::netio::exchange(88);
    fixture::hold();
    fixture::success("tcp_connect_88");
}
