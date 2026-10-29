// Target rule: Uncommon Process Access Rights For Target Image
// Sigma rule ID: 0d9cc92d-3ed8-beeb-dea9-8447f14fc31e
// Ruleset path: sigma/sysmon/process_access/proc_access_win_susp_all_access_uncommon_target.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE process_access_ping");if !fixture::begin("process_access_ping") {return;}
fixture::process_fixture::run(false);
fixture::success("process_access_ping");}
