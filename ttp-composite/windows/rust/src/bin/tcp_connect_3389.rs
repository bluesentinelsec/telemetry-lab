use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE tcp_connect_3389\n");
    if !fixture::begin("tcp_connect_3389") {
        fixture::hold();
        return;
    }
    use std::io::Write;
    let mut socket = fixture::netio::connect(3389);
    socket
        .write_all(&[3, 0, 0, 11, 6, 0xe0, 0, 0, 0, 0, 0])
        .unwrap();
    drop(socket);
    fixture::hold();
    fixture::success("tcp_connect_3389");
}
