//go:build linux || windows

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
// Enumerate the same platform root as the C and C++ implementations.

import (
	"os"
	"runtime"
)

func main() {
	root := "/"
	if runtime.GOOS == "windows" {
		root = `C:\`
	}
	entries, err := os.ReadDir(root)
	if err != nil {
		os.Exit(1)
	}
	if len(entries) == 0 {
		os.Exit(1)
	}
}
