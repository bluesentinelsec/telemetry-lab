//! read_sensitive_file composite (ATT&CK T1555) -- read /etc/shadow.
//!
//! A robustness control: an effect-keyed technique that should FIRE across every
//! substrate. Falco's "Read sensitive file untrusted" keys on an open-for-read
//! of a known-sensitive path (/etc/shadow), which is the same syscall regardless
//! of the runtime that issues it -- so no substrate should flip it. Benign: it
//! reads a few bytes and closes. Runs as root in the container, where
//! /etc/shadow is readable. Detonates in a container.

use std::fs::File;
use std::io::Read;

fn main() {
    // open("/etc/shadow", O_RDONLY): the fired syscall.
    let mut file = match File::open("/etc/shadow") {
        Ok(f) => f,
        Err(_) => std::process::exit(1),
    };
    let mut buf = [0u8; 64];
    let _ = file.read(&mut buf);
    // file dropped here -> closed.
}
