// Target rule: COM Hijacking via TreatAs
// Sigma rule ID: 6655602f-690f-f834-4dd4-c12213d0c687
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_treatas_persistence.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_com_treatas");if !fixture::begin("registry_com_treatas") {return;}
fixture::registry::set_verified("Software\\Classes\\CLSID\\{9B9C8026-806D-41E2-992A-909553D7A52A}\\TreatAs", "", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
fixture::success("registry_com_treatas");}
