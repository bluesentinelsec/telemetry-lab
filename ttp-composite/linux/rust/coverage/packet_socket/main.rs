fn main() {
    if !coverage_suite::begin("packet_socket") {
        return;
    }
    coverage_suite::packet_socket();
    println!("CASE_OK packet_socket");
}
