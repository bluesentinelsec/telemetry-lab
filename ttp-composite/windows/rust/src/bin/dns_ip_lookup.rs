use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_ip_lookup\n");
    if !fixture::begin("dns_ip_lookup") {
        fixture::hold();
        return;
    }
    fixture::netio::resolve("api.ipify.org");

    fixture::hold();
    fixture::success("dns_ip_lookup");
}
