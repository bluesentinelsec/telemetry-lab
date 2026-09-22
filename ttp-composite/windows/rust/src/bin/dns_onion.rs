use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_onion\n");
    if !fixture::begin("dns_onion") {
        return;
    }
    fixture::netio::resolve("lab.onion");

    fixture::success("dns_onion");
}
