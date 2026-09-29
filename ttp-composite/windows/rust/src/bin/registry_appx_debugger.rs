use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_appx_debugger");if !fixture::begin("registry_appx_debugger") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Windows\\CurrentVersion\\PackagedAppXDebug\\Microsoft.TelemetryLabFixture", "", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
fixture::success("registry_appx_debugger");}
