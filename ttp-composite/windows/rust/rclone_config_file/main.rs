// Target rule: Rclone Config File Creation
// Sigma rule ID: 1446e210-e8da-42a9-e7bf-8fb30a60366b
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_rclone_config_files.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE rclone_config_file");if !fixture::begin("rclone_config_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\text.txt", std::path::PathBuf::from("C:\\Users\\Public\\.config\\rclone\\telemetry-lab-fixture.conf"));
fixture::success("rclone_config_file");}
