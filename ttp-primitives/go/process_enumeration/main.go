//go:build linux

package main

// process_enumeration primitive: enumerate running processes.
//
// Discovery of other processes is a ubiquitous post-compromise primitive. On
// Linux the canonical mechanism is walking /proc: each numeric subdirectory is a
// live pid. This exercises the directory-read telemetry path against the kernel's
// process table (openat/getdents on /proc) rather than any single process event.
// Go's os.ReadDir is the direct-syscall equivalent of the C opendir/readdir walk;
// the cgo/static substrate split lives in anchor_cgo.go.
//
// Self-contained and read-only: it counts the numeric entries and exits 0 as
// long as at least itself is visible.
//
// Linux-only: Windows enumerates via Toolhelp32Snapshot (see issue #44).

import (
	"os"
)

func main() {
	entries, err := os.ReadDir("/proc")
	if err != nil {
		os.Exit(1)
	}
	pids := 0
	for _, e := range entries {
		if allDigits(e.Name()) {
			pids++
		}
	}
	if pids == 0 {
		os.Exit(1)
	}
}

func allDigits(s string) bool {
	if s == "" {
		return false
	}
	for _, r := range s {
		if r < '0' || r > '9' {
			return false
		}
	}
	return true
}
