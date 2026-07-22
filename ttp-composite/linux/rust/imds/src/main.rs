//! imds composite (ATT&CK T1552.005) -- EC2 Instance Metadata Service contact.
//!
//! A connect-seam probe: open a socket and connect to 169.254.169.254:80.
//! Falco's "Contact EC2 Instance Metadata Service From Container" keys on the
//! connect syscall's destination IP (fd.sip), not on success or on data read --
//! so it is expected to be ROBUST across substrates (a connect is a connect).
//! This is the cross-engine seam-catalog entry: it tests whether the PoC's
//! auditd Go non-blocking-connect evasion (which filtered on success=1)
//! generalizes to Falco. IMDS is reachable in the AWS lab.
//!
//! Benign: it only opens a connection and closes it; no credentials are read.
//! Detonates in a container.

use std::net::TcpStream;

fn main() {
    // The fired syscall: the connect to the IMDS link-local address. We ignore
    // the result -- Falco keys on the connect's destination IP, not on success.
    let _ = TcpStream::connect("169.254.169.254:80");
    // TcpStream drops here -> socket closed.
}
