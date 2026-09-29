use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_shortener\n");
    if !fixture::begin("dns_shortener") {
        return;
    }
    fixture::netio::resolve("tinyurl.com");

    fixture::success("dns_shortener");
}
