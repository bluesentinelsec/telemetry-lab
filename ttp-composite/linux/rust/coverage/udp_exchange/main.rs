fn main() {
    if !coverage_suite::begin("udp_exchange") {
        return;
    }
    coverage_suite::udp_exchange();
    println!("CASE_OK udp_exchange");
}
