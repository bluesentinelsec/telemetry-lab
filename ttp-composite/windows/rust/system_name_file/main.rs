// Target rule: Files With System Process Name In Unsuspected Locations
// Sigma rule ID: eccfe194-f618-b054-3986-7f7529f079f1
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_system_file.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE system_name_file");if !fixture::begin("system_name_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\svchost.exe"));
fixture::success("system_name_file");}
