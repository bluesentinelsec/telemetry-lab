fn main() {
    if !coverage_suite::begin("metadata_ec2") {
        return;
    }
    coverage_suite::metadata_exchange();
    println!("CASE_OK metadata_ec2");
}
