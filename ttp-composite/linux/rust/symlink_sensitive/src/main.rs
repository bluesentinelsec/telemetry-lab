//! symlink_sensitive composite (ATT&CK T1555) -- symlink over a sensitive file.
//!
//! A robustness control (effect-keyed, expected to FIRE on every substrate).
//! Falco's "Create Symlink Over Sensitive Files" keys on a symlink whose target
//! is a sensitive path (/etc/shadow). Benign: the link is created in /tmp and
//! removed immediately; /etc/shadow itself is untouched. Detonates in a
//! container.

use std::fs;
use std::os::unix::fs::symlink;

const LINK: &str = "/tmp/lab_shadow_link";

fn main() {
    // Clear any stale link from a prior run (ignore "not found").
    let _ = fs::remove_file(LINK);
    // symlink("/etc/shadow", "/tmp/lab_shadow_link"): the fired syscall.
    if symlink("/etc/shadow", LINK).is_err() {
        std::process::exit(1);
    }
    let _ = fs::remove_file(LINK);
}
