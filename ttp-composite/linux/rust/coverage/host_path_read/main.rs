use coverage_suite as fixture;
fn main() {if !fixture::begin("host_path_read") {return;}
fixture::read_file("/host/telemetry-lab/fixture");
println!("CASE_OK host_path_read");
}
