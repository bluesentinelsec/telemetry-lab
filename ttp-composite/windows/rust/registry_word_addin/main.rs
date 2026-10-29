// Target rule: Potential Persistence Via Visual Studio Tools for Office
// Sigma rule ID: ee69bf67-79f6-5973-f69d-7a6f609c97db
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_office_vsto.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_word_addin");if !fixture::begin("registry_word_addin") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Office\\Word\\Addins\\TelemetryLabFixture", "Manifest", "C:\\lab\\windows-coverage\\fixtures\\fixture.vsto");
fixture::success("registry_word_addin");}
