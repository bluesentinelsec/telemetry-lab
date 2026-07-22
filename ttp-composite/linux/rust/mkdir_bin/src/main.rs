//! mkdir_bin composite (ATT&CK T1222.002) -- create a directory in a binary path.
//!
//! A robustness control (effect-keyed, expected to FIRE on every substrate).
//! Falco's "Mkdir binary dirs" keys on creating a directory under a system
//! binary path (e.g. /usr/bin). Benign: the directory is empty and removed
//! immediately. Detonates in a container.

use std::fs;

const DIR: &str = "/usr/bin/lab_testdir";

fn main() {
    // Clear any stale directory from a prior run (ignore "not found").
    let _ = fs::remove_dir(DIR);
    // mkdir("/usr/bin/lab_testdir", 0755): the fired syscall.
    if fs::create_dir(DIR).is_err() {
        std::process::exit(1);
    }
    let _ = fs::remove_dir(DIR);
}
