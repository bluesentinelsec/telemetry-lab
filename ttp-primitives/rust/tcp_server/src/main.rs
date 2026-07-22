//! tcp_server primitive: accept a TCP connection and receive data.
//!
//! The measured behaviour is the server path: socket -> bind -> listen -> accept
//! -> recv -> send. A loopback client on 127.0.0.1 and an ephemeral port drives
//! the connection so the primitive is self-contained and offline. The exchange
//! is single-threaded: the client connects into the listen backlog, then the
//! server accepts, receives the request, and sends a reply. The client is
//! scaffolding; tcp_client is the primitive that emphasises it.
//!
//! Sockets are libc calls, so glibc vs musl is the axis under measurement.
//! Linux-only for this pass (Winsock on Windows -- issue #44).

use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn main() {
    let req = b"telemetry-lab\n";
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind loopback listener");
    let addr = listener.local_addr().expect("listener local addr");

    let mut client = TcpStream::connect(addr).expect("connect to loopback");
    let (mut server, _peer) = listener.accept().expect("accept connection");

    client.write_all(req).expect("client send");

    let mut buf = vec![0u8; req.len()];
    server.read_exact(&mut buf).expect("server recv");
    server.write_all(&buf).expect("server echo reply"); // echo reply

    let mut reply = vec![0u8; req.len()];
    client.read_exact(&mut reply).expect("client recv reply");
    std::process::exit(if reply == req { 0 } else { 1 });
}
