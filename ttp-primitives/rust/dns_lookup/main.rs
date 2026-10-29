//! dns_lookup primitive: resolve a hostname to addresses.
//!
//! Name resolution is a precursor to most network activity. `ToSocketAddrs` is
//! the standard resolver entry point; resolving "localhost" keeps the primitive
//! offline and deterministic (served from /etc/hosts / nsswitch, no DNS packet)
//! while still exercising the resolver telemetry path.
//!
//! The resolver lives in libc, so this is a strong glibc-vs-musl discriminator:
//! the two implement name resolution differently (NSS modules vs musl's built-in
//! resolver). Exits 0 when resolution yields at least one address.
//!
//! Linux-only for this pass (getaddrinfo via ws2tcpip on Windows -- issue #44).

use std::net::ToSocketAddrs;

fn main() {
    let addrs = ("localhost", 80u16).to_socket_addrs().expect("resolve localhost");
    let count = addrs.count();
    std::process::exit(if count >= 1 { 0 } else { 1 });
}
