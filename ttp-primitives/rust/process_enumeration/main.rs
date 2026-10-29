//! process_enumeration primitive: enumerate running processes.
//!
//! Discovery of other processes is a ubiquitous post-compromise primitive. On
//! Linux the canonical mechanism is walking /proc: each numeric subdirectory is
//! a live pid. This exercises the directory-read telemetry path against the
//! kernel's process table (openat/getdents on /proc) rather than any single
//! process event.
//!
//! Self-contained and read-only: it counts the numeric entries and exits 0 as
//! long as at least itself is visible.
//!
//! Linux-only: Windows enumerates via Toolhelp32Snapshot (see issue #44).

use std::fs;

fn main() {
    let entries = fs::read_dir("/proc").expect("open /proc");
    let mut pids = 0usize;
    for entry in entries.flatten() {
        let name = entry.file_name();
        let name = name.to_string_lossy();
        if !name.is_empty() && name.chars().all(|c| c.is_ascii_digit()) {
            pids += 1;
        }
    }
    std::process::exit(if pids > 0 { 0 } else { 1 });
}
