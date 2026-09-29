use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_hide_files");if !fixture::begin("registry_hide_files") {return;}
fixture::registry::set_dword("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden", 0);
fixture::success("registry_hide_files");}
