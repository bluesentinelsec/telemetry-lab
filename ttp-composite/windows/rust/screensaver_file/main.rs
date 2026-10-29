// Target rule: Suspicious Screensaver Binary File Creation
// Sigma rule ID: b7a6c875-41bf-5648-744f-d236cceb1c26
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_scr_binary_file.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE screensaver_file");if !fixture::begin("screensaver_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\fixture.scr"));
fixture::success("screensaver_file");}
