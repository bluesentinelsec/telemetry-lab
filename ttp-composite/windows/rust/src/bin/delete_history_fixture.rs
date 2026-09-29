use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE delete_history_fixture");if !fixture::begin("delete_history_fixture") {return;}
let path=std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\PSReadLine\\ConsoleHost_history.txt");std::fs::remove_file(&path).unwrap();assert_eq!(std::fs::metadata(&path).unwrap_err().kind(),std::io::ErrorKind::NotFound);
fixture::success("delete_history_fixture");}
