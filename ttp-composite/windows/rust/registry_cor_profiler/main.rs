// Target rule: Enabling COR Profiler Environment Variables
// Sigma rule ID: aeac22f7-e219-1561-df1f-f531ac2d096f
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_enabling_cor_profiler_env_variables.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_cor_profiler");if !fixture::begin("registry_cor_profiler") {return;}
fixture::registry::set_verified("Environment", "COR_PROFILER", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
fixture::success("registry_cor_profiler");}
