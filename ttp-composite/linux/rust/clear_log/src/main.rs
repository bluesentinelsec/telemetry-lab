//! clear_log composite (ATT&CK T1070) -- truncate a file under /var/log.
//!
//! A robustness control (effect-keyed, expected to FIRE on every substrate).
//! Falco's "Clear Log Activities" keys on opening a file in a log directory with
//! truncation. Benign: it creates and truncates its own file under /var/log and
//! removes it -- no real log is destroyed. Detonates in a container.

use std::fs::{self, OpenOptions};

const LOG: &str = "/var/log/lab_clear.log";

fn main() {
    // open(LOG, O_WRONLY|O_CREAT|O_TRUNC, 0644): the fired syscall (truncation
    // in a log directory). write(true)+create(true)+truncate(true) mirrors it.
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(LOG);
    if file.is_err() {
        std::process::exit(1);
    }
    drop(file); // close before unlink.
    let _ = fs::remove_file(LOG);
}
