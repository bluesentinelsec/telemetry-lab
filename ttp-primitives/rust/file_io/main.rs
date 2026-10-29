//! file_io primitive: write a temporary file and read it back. Self-contained
//! (creates its own temp file). Exercises the file-I/O telemetry family.

use std::env;
use std::fs;

fn main() {
    let path = env::temp_dir().join("ttp_file_io.dat");
    fs::write(&path, b"telemetry-lab\n").expect("write temp file");
    let _contents = fs::read(&path).expect("read temp file");
    let _ = fs::remove_file(&path);
}
