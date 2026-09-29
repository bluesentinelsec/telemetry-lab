use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE delete_zone_identifier");if !fixture::begin("delete_zone_identifier") {return;}
let path=std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier");assert_eq!(std::fs::read(&path).unwrap()[0], b'[');
std::fs::remove_file(&path).unwrap();
assert_eq!(std::fs::File::open(&path).unwrap_err().kind(),std::io::ErrorKind::NotFound);
assert!(std::path::Path::new("C:\\lab\\windows-coverage\\work\\download.txt").is_file());
fixture::success("delete_zone_identifier");}
