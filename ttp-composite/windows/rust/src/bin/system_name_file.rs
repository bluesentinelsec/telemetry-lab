use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE system_name_file");if !fixture::begin("system_name_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\svchost.exe"));
fixture::success("system_name_file");}
