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
