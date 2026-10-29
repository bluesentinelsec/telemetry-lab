// Target rule: Potential File Extension Spoofing Using Right-to-Left Override
// Sigma rule ID: 1522de8d-352b-1bb8-509b-932d2dd4bb60
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_right_to_left_override_extension_spoofing.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE rtlo_file");if !fixture::begin("rtlo_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\report\u{202e}fdp.exe"));
fixture::success("rtlo_file");}
