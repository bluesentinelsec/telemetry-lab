use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_logon_script");if !fixture::begin("registry_logon_script") {return;}
fixture::registry::set_verified("Environment", "UserInitMprLogonScript", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
fixture::success("registry_logon_script");}
