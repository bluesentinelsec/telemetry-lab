use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE screensaver_file");if !fixture::begin("screensaver_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\fixture.scr"));
fixture::success("screensaver_file");}
