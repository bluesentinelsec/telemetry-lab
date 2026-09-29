use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_appcompat_restart");if !fixture::begin("registry_appcompat_restart") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers", "C:\\lab\\windows-coverage\\fixtures\\helper.exe", "REGISTERAPPRESTART");
fixture::success("registry_appcompat_restart");}
