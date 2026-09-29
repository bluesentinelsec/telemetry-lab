use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_office_macro");if !fixture::begin("registry_office_macro") {return;}
fixture::registry::set_dword("Software\\Microsoft\\Office\\16.0\\Word\\Security", "VBAWarnings", 1);
fixture::success("registry_office_macro");}
