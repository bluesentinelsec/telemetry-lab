use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE delete_zone_identifier");if !fixture::begin("delete_zone_identifier") {return;}
let path=std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier");std::fs::remove_file(&path).unwrap();assert_eq!(std::fs::metadata(&path).unwrap_err().kind(),std::io::ErrorKind::NotFound);
fixture::success("delete_zone_identifier");}
