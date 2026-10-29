// Target rule: Network Connection Initiated From Process Located In Potentially Suspicious Or Uncommon Location
// Sigma rule ID: df13f270-859b-272a-9c2a-a0ef744a0480
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_initiated_uncommon_or_suspicious_locations.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE tcp_connect_public_path\n");
    if !fixture::begin("tcp_connect_public_path") {
        fixture::hold();
        return;
    }
    assert_eq!(
        std::env::current_exe()
            .unwrap()
            .to_str()
            .unwrap()
            .to_ascii_lowercase(),
        r"c:\users\public\telemetry-lab\probe.exe"
    );
    fixture::netio::exchange(49152);
    fixture::hold();
    fixture::success("tcp_connect_public_path");
}
