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
