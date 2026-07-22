//go:build linux

package main

// pipe_ipc primitive: pass a message through an anonymous pipe.
//
// Inter-process communication via an anonymous pipe: create the pipe, write a
// fixed message to the write end, read it back from the read end, verify it
// round-tripped. Exercises the pipe/read/write telemetry family. This is the
// same pipe machinery a runtime's os/exec relay uses, so it is a natural
// substrate discriminator (the Go reverse-shell mover keys on exactly this).
// os.Pipe is the direct pipe(2) wrapper; the cgo/static split lives in
// anchor_cgo.go. (Go's os.Pipe has none of the std::io::pipe concerns; it is a
// plain pipe pair.)
//
// Self-contained and deterministic (its own pipe, fixed payload). pipe() is
// POSIX; Windows uses CreatePipe/_pipe (issue #44).

import (
	"bytes"
	"io"
	"os"
)

func main() {
	r, w, err := os.Pipe()
	if err != nil {
		os.Exit(1)
	}
	msg := []byte("telemetry-lab\n")
	if _, err := w.Write(msg); err != nil {
		os.Exit(1)
	}
	buf := make([]byte, len(msg))
	if _, err := io.ReadFull(r, buf); err != nil {
		os.Exit(1)
	}
	r.Close()
	w.Close()
	if !bytes.Equal(buf, msg) {
		os.Exit(1)
	}
}
