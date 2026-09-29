use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_word_addin");if !fixture::begin("registry_word_addin") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Office\\Word\\Addins\\TelemetryLabFixture", "Manifest", "C:\\lab\\windows-coverage\\fixtures\\fixture.vsto");
fixture::success("registry_word_addin");}
