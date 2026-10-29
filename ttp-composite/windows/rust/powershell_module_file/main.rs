// Target rule: PowerShell Module File Created By Non-PowerShell Process
// Sigma rule ID: 103362bb-15b7-3bed-7f8c-fd7a15fe31f4
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_powershell_module_uncommon_creation.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE powershell_module_file");if !fixture::begin("powershell_module_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\text.txt", std::path::PathBuf::from(std::env::var_os("USERPROFILE").unwrap()).join("Documents\\WindowsPowerShell\\Modules\\TelemetryLabFixture\\TelemetryLabFixture.psm1"));
fixture::success("powershell_module_file");}
