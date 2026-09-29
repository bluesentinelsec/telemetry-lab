use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE errorhandler_file");if !fixture::begin("errorhandler_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\text.txt", std::path::PathBuf::from("C:\\Windows\\Setup\\Scripts\\ErrorHandler.cmd"));
fixture::success("errorhandler_file");}
