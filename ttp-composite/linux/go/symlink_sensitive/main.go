// symlink_sensitive composite (ATT&CK T1555) -- symlink over a sensitive file.
//
// Robustness control (expected to FIRE on every substrate): Falco's "Create
// Symlink Over Sensitive Files" keys on a symlink whose target is /etc/shadow.
// Benign: the link is created in /tmp and removed; /etc/shadow is untouched.
package main

import "os"

func main() {
	os.Remove("/tmp/lab_shadow_link")
	if os.Symlink("/etc/shadow", "/tmp/lab_shadow_link") != nil {
		return
	}
	os.Remove("/tmp/lab_shadow_link")
}
