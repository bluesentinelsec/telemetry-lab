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
