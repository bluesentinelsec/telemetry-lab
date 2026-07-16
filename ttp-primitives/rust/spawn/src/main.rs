//! spawn primitive: create a child process and wait for it. Exercises the
//! process-lifecycle telemetry family. The no-op command differs per OS but the
//! behaviour -- create and reap a child -- is equivalent.

use std::process::Command;

fn main() {
    let status = if cfg!(windows) {
        Command::new("cmd").args(["/c", "exit"]).status()
    } else {
        Command::new("true").status()
    }
    .expect("failed to spawn child process");

    std::process::exit(status.code().unwrap_or(1));
}
