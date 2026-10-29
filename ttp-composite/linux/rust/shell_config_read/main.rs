// Target rule: Read Shell Configuration File
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main(){if !coverage_suite::begin("shell_config_read"){return;}
coverage_suite::read_file("/root/.bashrc");
println!("CASE_OK shell_config_read");}
