use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_suspicious_env");if !fixture::begin("registry_suspicious_env") {return;}
fixture::registry::set_verified("Environment", "TelemetryLabFixture", "C:\\Users\\Public\\telemetry-lab\\fixture.exe");
fixture::success("registry_suspicious_env");}
