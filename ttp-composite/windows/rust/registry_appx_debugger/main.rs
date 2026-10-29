// Target rule: Potential Persistence Using DebugPath
// Sigma rule ID: 1fa31aa7-117f-4356-a2ab-7062be19c8a6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_appx_debugger.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_appx_debugger");if !fixture::begin("registry_appx_debugger") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Windows\\CurrentVersion\\PackagedAppXDebug\\Microsoft.TelemetryLabFixture", "", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
fixture::success("registry_appx_debugger");}
