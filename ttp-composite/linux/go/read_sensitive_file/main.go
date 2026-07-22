// read_sensitive_file composite (ATT&CK T1555) -- read /etc/shadow.
//
// Robustness control (expected to FIRE on every substrate): Falco's "Read
// sensitive file untrusted" keys on an open-for-read of /etc/shadow, the same
// syscall regardless of runtime. Benign: reads a few bytes and closes.
package main

import "os"

func main() {
	f, err := os.Open("/etc/shadow")
	if err != nil {
		return
	}
	buf := make([]byte, 64)
	f.Read(buf)
	f.Close()
}
