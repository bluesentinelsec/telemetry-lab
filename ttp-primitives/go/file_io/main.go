package main

// file_io primitive: write a temporary file and read it back. Self-contained
// (creates its own temp file). Exercises the file-I/O telemetry family.
// The cgo-linkage concession that makes this a valid discriminator for the CGO
// on/off substrate axis lives in anchor_cgo.go (compiled only when cgo is on):
// Go file I/O uses direct syscalls, not cgo, so the axis needs the anchor.

import "os"

func main() {
	f, err := os.CreateTemp("", "ttp_file_io_*.dat")
	if err != nil {
		os.Exit(1)
	}
	name := f.Name()
	if _, err := f.WriteString("telemetry-lab\n"); err != nil {
		os.Exit(1)
	}
	f.Close()
	if _, err := os.ReadFile(name); err != nil {
		os.Exit(1)
	}
	os.Remove(name)
}
