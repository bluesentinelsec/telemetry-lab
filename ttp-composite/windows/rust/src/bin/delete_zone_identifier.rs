use windows_detection_composites as fixture;
use std::io::ErrorKind;
use std::time::{Duration, Instant};

fn main() {
    println!("COMPOSITE_CASE delete_zone_identifier");
    if !fixture::begin("delete_zone_identifier") { return; }
    let path = std::path::PathBuf::from("C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier");
    assert_eq!(std::fs::read(&path).unwrap()[0], b'[');
    std::fs::remove_file(&path).unwrap();
    // Verify completion, without repeating deletion or retaining probe handles.
    let started = Instant::now();
    let mut probes = 0;
    loop {
        probes += 1;
        match std::fs::File::open(&path) {
            Ok(file) => drop(file),
            Err(error) if error.kind() == ErrorKind::NotFound => break,
            Err(error) => assert_eq!(error.kind(), ErrorKind::PermissionDenied),
        }
        assert!(started.elapsed() < Duration::from_secs(5), "stream deletion did not complete");
        std::thread::sleep(Duration::from_millis(10));
    }
    println!("STREAM_ABSENT probes={} elapsed_ms={}", probes, started.elapsed().as_millis());
    assert!(std::path::Path::new("C:\\lab\\windows-coverage\\work\\download.txt").is_file());
    fixture::success("delete_zone_identifier");
}
