// Target rule: Container Drift Detected (chmod)
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
use std::os::unix::fs::{PermissionsExt};
fn main(){if !coverage_suite::begin("executable_chmod"){return;}
std::fs::set_permissions("/tmp/lab/executable-mode",std::fs::Permissions::from_mode(0o700)).unwrap();
assert_eq!(std::fs::metadata("/tmp/lab/executable-mode").unwrap().permissions().mode()&0o777,0o700);
println!("CASE_OK executable_chmod");}
