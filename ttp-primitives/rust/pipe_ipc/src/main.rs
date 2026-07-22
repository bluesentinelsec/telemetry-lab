//! pipe_ipc primitive: pass a message through an anonymous pipe.
//!
//! Inter-process communication via an anonymous pipe: create the pipe, write a
//! fixed message to the write end, read it back from the read end, verify it
//! round-tripped. Exercises the pipe/read/write telemetry family. This is the
//! same pipe machinery a runtime's process relay uses, so it is a natural
//! substrate discriminator (the Go reverse-shell mover keys on exactly this).
//!
//! Self-contained and deterministic (its own pipe, fixed payload). Uses
//! `std::io::pipe` (stable since Rust 1.87); Windows uses CreatePipe (issue #44).

use std::io::{Read, Write};

fn main() {
    let msg = b"telemetry-lab\n";
    let (mut reader, mut writer) = std::io::pipe().expect("create pipe");
    writer.write_all(msg).expect("write to pipe");
    // Drop the writer so the read side sees EOF and read_exact can complete.
    drop(writer);

    let mut buf = vec![0u8; msg.len()];
    reader.read_exact(&mut buf).expect("read from pipe");
    std::process::exit(if buf == msg { 0 } else { 1 });
}
