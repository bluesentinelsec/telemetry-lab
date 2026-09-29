use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE shim_database_file");if !fixture::begin("shim_database_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\text.txt", std::path::PathBuf::from("C:\\Windows\\AppPatch\\Custom\\telemetry-lab-fixture.sdb"));
fixture::success("shim_database_file");}
