// Target rule: Files With System DLL Name In Unsuspected Locations
// Sigma rule ID: 47b821bf-c853-813b-eaa2-be2620f42a1d
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_system_dll_files.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE system_dll_file");if !fixture::begin("system_dll_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\fixture.node", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\secur32.dll"));
fixture::success("system_dll_file");}
