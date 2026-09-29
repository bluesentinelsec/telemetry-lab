use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_com_treatas");if !fixture::begin("registry_com_treatas") {return;}
fixture::registry::set_verified("Software\\Classes\\CLSID\\{9B9C8026-806D-41E2-992A-909553D7A52A}\\TreatAs", "", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
fixture::success("registry_com_treatas");}
