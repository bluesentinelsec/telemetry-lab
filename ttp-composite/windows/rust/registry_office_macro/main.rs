// Target rule: Office Macros Warning Disabled
// Sigma rule ID: 8b6b4194-cfe8-b585-475f-5997e8015fe0
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_office_vba_warnings_tamper.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_office_macro");if !fixture::begin("registry_office_macro") {return;}
fixture::registry::set_dword("Software\\Microsoft\\Office\\16.0\\Word\\Security", "VBAWarnings", 1);
fixture::success("registry_office_macro");}
