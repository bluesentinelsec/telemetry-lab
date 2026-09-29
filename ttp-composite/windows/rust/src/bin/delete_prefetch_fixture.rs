use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE delete_prefetch_fixture");if !fixture::begin("delete_prefetch_fixture") {return;}
let path=std::path::PathBuf::from("C:\\Windows\\Prefetch\\TELEMETRYLABFIXTURE.pf");std::fs::remove_file(&path).unwrap();assert_eq!(std::fs::metadata(&path).unwrap_err().kind(),std::io::ErrorKind::NotFound);
fixture::success("delete_prefetch_fixture");}
