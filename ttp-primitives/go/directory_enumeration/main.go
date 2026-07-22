//go:build linux

package main

// directory_enumeration primitive: list the entries of a directory.
//
// Filesystem discovery -- listing a directory -- is a recurring reconnaissance
// primitive. It exercises the directory-read telemetry path (openat + getdents)
// distinctly from file_io's open/read/write of a single file. The root
// directory "/" is always present and read-only here, so the primitive is
// deterministic and needs no setup. Go's os.ReadDir is the direct-syscall
// equivalent of the C opendir/readdir walk; the cgo/static substrate split
// lives in anchor_cgo.go.
//
// Linux-only for this pass (portable via FindFirstFile / std::filesystem on
// Windows -- issue #44).

import (
	"os"
)

func main() {
	entries, err := os.ReadDir("/")
	if err != nil {
		os.Exit(1)
	}
	if len(entries) == 0 {
		os.Exit(1)
	}
}
