use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE perflogs_file");if !fixture::begin("perflogs_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\helper.exe", std::path::PathBuf::from("C:\\PerfLogs\\telemetry-lab\\fixture.exe"));
fixture::success("perflogs_file");}
