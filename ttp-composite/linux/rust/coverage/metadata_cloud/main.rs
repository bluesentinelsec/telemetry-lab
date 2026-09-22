fn main() {
    if !coverage_suite::begin("metadata_cloud") {
        return;
    }
    coverage_suite::metadata_exchange();
    println!("CASE_OK metadata_cloud");
}
