use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE system_dll_file");if !fixture::begin("system_dll_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\fixture.node", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\secur32.dll"));
fixture::success("system_dll_file");}
