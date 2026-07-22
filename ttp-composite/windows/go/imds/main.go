//go:build windows

// imds composite (ATT&CK T1552.005) -- connect to the cloud metadata service,
// the Windows analog of the Linux Go imds.
//
// Sysmon EID 3 (Network Connect). Expected ROBUST: Sysmon keys on the
// connection's destination address (169.254.169.254), not on whether the
// request succeeds or on any application-layer read, so a runtime substrate
// should not flip it. Benign: dial and close, no credentials are read.
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
