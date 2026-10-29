// Target rule: Potential Persistence Via TypedPaths
// Sigma rule ID: a1229092-bf43-58f9-b9b4-f8fc3da816e6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_typed_paths.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_typed_paths");if !fixture::begin("registry_typed_paths") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths", "url99", "C:\\lab\\windows-coverage\\work");
fixture::success("registry_typed_paths");}
