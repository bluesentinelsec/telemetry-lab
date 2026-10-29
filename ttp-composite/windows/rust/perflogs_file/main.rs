// Target rule: Suspicious File Created In PerfLogs
// Sigma rule ID: 8822f47b-fcbf-b189-f9a1-10961c8f7cd0
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_perflogs_susp_files.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE perflogs_file");if !fixture::begin("perflogs_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\PerfLogs\\telemetry-lab\\fixture.exe"));
fixture::success("perflogs_file");}
