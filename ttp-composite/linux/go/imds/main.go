// imds composite (ATT&CK T1552.005) -- connect to the EC2 metadata service.
//
// Connect-seam probe (expected ROBUST): dial 169.254.169.254:80. Falco keys on
// the connect syscall's destination IP (fd.sip), not on success, so a substrate
// should not flip it. Tests whether the PoC's auditd Go non-blocking-connect
// evasion generalizes to Falco. Benign: connect and close, no credentials read.
package main

import (
	"net"
	"time"
)

func main() {
	conn, err := net.DialTimeout("tcp", "169.254.169.254:80", 2*time.Second)
	if err == nil {
		conn.Close()
	}
}
