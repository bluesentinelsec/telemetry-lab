//! directory_enumeration primitive: list the entries of a directory.
//!
//! Filesystem discovery -- listing a directory -- is a recurring reconnaissance
//! primitive. It exercises the directory-read telemetry path (openat + getdents)
//! distinctly from file_io's open/read/write of a single file. The root
//! directory "/" is always present and read-only here, so the primitive is
//! deterministic and needs no setup.
//!
//! Linux-only for this pass (portable via std::fs::read_dir on Windows --
//! issue #44).

use std::fs;

fn main() {
    let entries = fs::read_dir("/").expect("open /");
    let count = entries.flatten().count();
    std::process::exit(if count > 0 { 0 } else { 1 });
}
