// Target rule: Displaying Hidden Files Feature Disabled
// Sigma rule ID: 96cd46a9-33dc-28dc-273e-83bc1fd8adc9
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_hide_file.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_hide_files");if !fixture::begin("registry_hide_files") {return;}
fixture::registry::set_dword("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden", 0);
fixture::success("registry_hide_files");}
