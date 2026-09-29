use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE rclone_config_file");if !fixture::begin("rclone_config_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\text.txt", std::path::PathBuf::from(std::env::var_os("USERPROFILE").unwrap()).join(".config\\rclone\\telemetry-lab-fixture.conf"));
fixture::success("rclone_config_file");}
