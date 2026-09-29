use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE rtlo_file");if !fixture::begin("rtlo_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\report‮fdp.exe"));
fixture::success("rtlo_file");}
