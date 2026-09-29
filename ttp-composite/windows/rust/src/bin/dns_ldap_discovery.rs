use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE dns_ldap_discovery\n");
    if !fixture::begin("dns_ldap_discovery") {
        return;
    }
    fixture::netio::resolve("_ldap.telemetry-lab.test");

    fixture::success("dns_ldap_discovery");
}
