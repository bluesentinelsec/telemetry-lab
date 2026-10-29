// Target rule: Create Hidden Files or Directories
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main(){if !coverage_suite::begin("hidden_file"){return;}
coverage_suite::write_file("/tmp/lab/.hidden-fixture"); coverage_suite::read_file("/tmp/lab/.hidden-fixture");
println!("CASE_OK hidden_file");}
