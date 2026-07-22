//! tcp_client primitive: open a TCP connection and send data.
//!
//! The measured behaviour is the client path: socket -> connect -> send -> recv.
//! To stay self-contained and offline, the primitive also opens a loopback
//! listener on 127.0.0.1 and an ephemeral port and drives the exchange against
//! itself -- no external host, no fixed port. A blocking connect to a listening
//! socket completes via the kernel's accept backlog, so the whole exchange runs
//! single-threaded (no thread-creation telemetry to confound the socket path).
//! The listener is scaffolding; tcp_server is the primitive that emphasises it.
//!
//! Sockets are libc calls, so glibc vs musl is the axis under measurement.
//! Linux-only for this pass (Winsock on Windows -- issue #44).

use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn main() {
    let msg = b"telemetry-lab\n";
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind loopback listener");
    let addr = listener.local_addr().expect("listener local addr");

    let mut client = TcpStream::connect(addr).expect("connect to loopback");
    let (mut server, _peer) = listener.accept().expect("accept connection");

    client.write_all(msg).expect("client send");

    let mut buf = vec![0u8; msg.len()];
    server.read_exact(&mut buf).expect("server recv");
    std::process::exit(if buf == msg { 0 } else { 1 });
}
