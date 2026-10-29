// Target rule: Suspicious Environment Variable Has Been Registered
// Sigma rule ID: eca534f8-005d-bb79-798d-0af4e2bf38d6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_suspicious_env_variables.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_suspicious_env");if !fixture::begin("registry_suspicious_env") {return;}
fixture::registry::set_verified("Environment", "TelemetryLabFixture", "C:\\Users\\Public\\telemetry-lab\\fixture.exe");
fixture::success("registry_suspicious_env");}
