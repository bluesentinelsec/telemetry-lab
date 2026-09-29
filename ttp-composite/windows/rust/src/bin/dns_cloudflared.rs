use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_cloudflared\n");
    if !fixture::begin("dns_cloudflared") {
        fixture::hold();
        return;
    }
    fixture::netio::resolve("protocol-v2.argotunnel.com");

    fixture::hold();
    fixture::success("dns_cloudflared");
}
