// Target rule: Potential Persistence Via Logon Scripts - Registry
// Sigma rule ID: aadaadd9-d82e-918a-20ca-01a4f35cde1f
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_logon_scripts_userinitmprlogonscript.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_logon_script");if !fixture::begin("registry_logon_script") {return;}
fixture::registry::set_verified("Environment", "UserInitMprLogonScript", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
fixture::success("registry_logon_script");}
