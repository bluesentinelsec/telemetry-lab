// Target rule: Container Access to Host Sensitive Paths
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
use coverage_suite as fixture;
fn main() {if !fixture::begin("host_path_read") {return;}
fixture::read_file("/host/telemetry-lab/fixture");
println!("CASE_OK host_path_read");
}
