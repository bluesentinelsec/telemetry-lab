// mkdir_bin composite (ATT&CK T1222.002) -- create a directory in a binary path.
//
// Robustness control (expected to FIRE on every substrate): Falco's "Mkdir
// binary dirs" keys on creating a directory under a system binary path. Benign:
// the directory is empty and removed immediately.
package main

import "os"

func main() {
	os.Remove("/usr/bin/lab_testdir")
	if os.Mkdir("/usr/bin/lab_testdir", 0755) != nil {
		return
	}
	os.Remove("/usr/bin/lab_testdir")
}
