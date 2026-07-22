//! http_client primitive: perform HTTP GET and POST requests.
//!
//! HTTP is the most common application-layer channel for staging and C2. The
//! request/response is hand-rolled over a raw TCP socket -- no HTTP or TLS
//! library -- so the primitive adds no third-party runtime and works on every
//! substrate including musl and static builds (see issue #43 for why the TLS
//! https_client is deferred). It stays self-contained and offline by talking to
//! a loopback responder on 127.0.0.1 and an ephemeral port, single-threaded via
//! the listen backlog. Both a GET and a POST are issued to exercise both methods.
//!
//! At the syscall level this is the tcp_client path plus HTTP framing in the
//! payload; the point is the request/response round-trip, not a full HTTP client.
//! Linux-only for this pass (Winsock on Windows -- issue #44).

use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener, TcpStream};

/// One full HTTP exchange over loopback: client sends `request`, server reads it
/// and replies, client reads the reply. Both ends stay open throughout, so no
/// send races a closed peer. Returns true on success.
fn exchange(listener: &TcpListener, addr: SocketAddr, request: &[u8]) -> bool {
    let mut client = match TcpStream::connect(addr) {
        Ok(c) => c,
        Err(_) => return false,
    };
    let mut server = match listener.accept() {
        Ok((s, _peer)) => s,
        Err(_) => return false,
    };

    if client.write_all(request).is_err() {
        return false;
    }

    let mut buf = [0u8; 512];
    if !matches!(server.read(&mut buf), Ok(n) if n > 0) {
        return false; // server reads the request
    }

    let resp = b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok";
    if server.write_all(resp).is_err() {
        return false;
    }

    matches!(client.read(&mut buf), Ok(n) if n > 0) // client reads the response
}

fn main() {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind loopback listener");
    let addr = listener.local_addr().expect("listener local addr");

    let get = b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n";
    let post = b"POST / HTTP/1.0\r\nHost: localhost\r\nContent-Length: 14\r\n\r\ntelemetry-lab\n";

    let ok = exchange(&listener, addr, get) && exchange(&listener, addr, post);
    std::process::exit(if ok { 0 } else { 1 });
}
