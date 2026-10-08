use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
fn main(){if !coverage_suite::begin("executable_create"){return;}
drop(std::fs::OpenOptions::new().write(true).create_new(true).mode(0o700).open("/tmp/lab/executable-new").unwrap());
assert_eq!(std::fs::metadata("/tmp/lab/executable-new").unwrap().permissions().mode()&0o777,0o700);
println!("CASE_OK executable_create");}
