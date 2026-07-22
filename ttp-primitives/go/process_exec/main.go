//go:build linux

package main

// process_exec primitive: replace the current process image with a no-op.
//
// Distinct from `spawn` (which forks a child and reaps it): exec-family calls
// REPLACE the calling image in place, so no new pid is created and control never
// returns on success. This exercises the execve telemetry path without the
// fork/clone that spawn emits -- a different process-lifecycle signal. Go's
// syscall.Exec is the direct execve wrapper, so it matches the C execlp path.
// The cgo/static substrate split lives in anchor_cgo.go.
//
// Linux-only: Windows has no true exec-replace semantic (see issue #44).

import (
	"os"
	"os/exec"
	"syscall"
)

func main() {
	p, err := exec.LookPath("true")
	if err != nil {
		os.Exit(1)
	}
	// syscall.Exec replaces this image; on success it never returns and the
	// exit status of `true` (0) becomes the primitive's.
	if err := syscall.Exec(p, []string{"true"}, os.Environ()); err != nil {
		os.Exit(1)
	}
}
