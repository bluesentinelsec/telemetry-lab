use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE registry_cor_profiler");if !fixture::begin("registry_cor_profiler") {return;}
fixture::registry::set_verified("Environment", "COR_PROFILER", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
fixture::success("registry_cor_profiler");}
