package main

// spawn primitive: create a child process and wait for it. Exercises the
// process-lifecycle telemetry family and the monitor's process-tree following.
// The no-op command differs per OS but the behaviour is equivalent. Go's os/exec
// uses direct syscalls (not cgo), so the CGO substrate axis needs anchor_cgo.go.

import (
	"os"
	"os/exec"
	"runtime"
)

func main() {
	var cmd *exec.Cmd
	if runtime.GOOS == "windows" {
		cmd = exec.Command("cmd", "/c", "exit")
	} else {
		cmd = exec.Command("true")
	}
	if err := cmd.Run(); err != nil {
		os.Exit(1)
	}
}
