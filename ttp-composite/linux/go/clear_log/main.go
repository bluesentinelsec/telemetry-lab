// clear_log composite (ATT&CK T1070) -- truncate a file under /var/log.
//
// Robustness control (expected to FIRE on every substrate): Falco's "Clear Log
// Activities" keys on opening a log-directory file with truncation. Benign: it
// creates, truncates, and removes its own file under /var/log.
package main

import "os"

func main() {
	f, err := os.OpenFile("/var/log/lab_clear.log", os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		return
	}
	f.Close()
	os.Remove("/var/log/lab_clear.log")
}
