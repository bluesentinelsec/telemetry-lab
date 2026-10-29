// Target rule: Potential Persistence Via AppCompat RegisterAppRestart Layer
// Sigma rule ID: 349ed81d-2f2f-a95f-2d5d-41e5fbeaf784
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_app_cpmpat_layer_registerapprestart.yml
use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_appcompat_restart");if !fixture::begin("registry_appcompat_restart") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers", "C:\\lab\\windows-coverage\\fixtures\\helper.exe", "REGISTERAPPRESTART");
fixture::success("registry_appcompat_restart");}
