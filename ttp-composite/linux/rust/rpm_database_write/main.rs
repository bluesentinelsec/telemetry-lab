// Target rule: Write below rpm database
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
use coverage_suite as fixture;
fn main() {if !fixture::begin("rpm_database_write") {return;}
fixture::write_file("/var/lib/rpm/telemetry-lab-fixture");
println!("CASE_OK rpm_database_write");
}
