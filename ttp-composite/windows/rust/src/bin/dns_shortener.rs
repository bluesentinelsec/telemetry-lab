use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_shortener\n");
    if !fixture::begin("dns_shortener") {
        fixture::hold();
        return;
    }
    fixture::netio::resolve("tinyurl.com");

    fixture::hold();
    fixture::success("dns_shortener");
}
