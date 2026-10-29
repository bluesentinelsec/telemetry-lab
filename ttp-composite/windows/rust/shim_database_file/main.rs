// Target rule: New Custom Shim Database Created
// Sigma rule ID: 4211e288-60d6-2bb1-01c3-b7b3191126a9
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_new_shim_database.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE shim_database_file");if !fixture::begin("shim_database_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\text.txt", std::path::PathBuf::from("C:\\Windows\\AppPatch\\Custom\\telemetry-lab-fixture.sdb"));
fixture::success("shim_database_file");}
