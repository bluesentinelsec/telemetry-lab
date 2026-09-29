use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_typed_paths");if !fixture::begin("registry_typed_paths") {return;}
fixture::registry::set_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths", "url99", "C:\\lab\\windows-coverage\\work");
fixture::success("registry_typed_paths");}
