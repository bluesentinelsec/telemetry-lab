use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_remote_access\n");
    if !fixture::begin("dns_remote_access") {
        return;
    }
    fixture::netio::resolve("api.splashtop.com");

    fixture::success("dns_remote_access");
}
