// Target rule: Remote Thread Creation In Uncommon Target Image
// Sigma rule ID: 43e75355-271c-2069-4eca-cc2e117f8510
// Ruleset path: sigma/sysmon/create_remote_thread/create_remote_thread_win_susp_uncommon_target_image.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE remote_thread_ping");if !fixture::begin("remote_thread_ping") {return;}
fixture::process_fixture::run(true);
fixture::success("remote_thread_ping");}
