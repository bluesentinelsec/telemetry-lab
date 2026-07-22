//go:build windows

// startup_folder composite (ATT&CK T1547.001) -- Startup folder persistence.
//
// Sysmon EID 11 (File Create). Expected ROBUST: Sysmon keys on a file being
// created under the per-user Startup folder, so the write fires the event no
// matter which runtime performs it. std-only (os.WriteFile / os.Remove). Benign:
// a few placeholder bytes are written to lab_test.lnk and removed immediately --
// it is not a real shortcut and is never launched.
package main

import (
	"os"
	"path/filepath"
)

func main() {
	appdata := os.Getenv("APPDATA")
	if appdata == "" {
		return
	}
	path := filepath.Join(appdata,
		"Microsoft", "Windows", "Start Menu", "Programs", "Startup", "lab_test.lnk")

	if err := os.WriteFile(path, []byte("lab_test"), 0644); err != nil {
		return
	}
	os.Remove(path)
}
