//go:build linux

package main

// tcp_client primitive: open a TCP connection and send data.
//
// The measured behaviour is the client path: dial -> write -> (server reads).
// To stay self-contained and offline, the primitive also opens a loopback
// listener on 127.0.0.1 and an ephemeral port and drives the exchange against
// itself -- no external host, no fixed port. A blocking dial to a listening
// socket completes via the kernel's accept backlog, so the whole exchange runs
// single-threaded (no thread-creation telemetry to confound the socket path).
// The listener is scaffolding; tcp_server is the primitive that emphasises it.
//
// Sockets are libc calls under cgo, so the cgo/static split is the axis under
// measurement; the anchor lives in anchor_cgo.go.
// Linux-only for this pass (Winsock on Windows -- issue #44).

import (
	"io"
	"net"
	"os"
)

func main() {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		os.Exit(1)
	}
	defer ln.Close()

	cli, err := net.Dial("tcp", ln.Addr().String())
	if err != nil {
		os.Exit(1)
	}
	defer cli.Close()

	srv, err := ln.Accept()
	if err != nil {
		os.Exit(1)
	}
	defer srv.Close()

	msg := []byte("telemetry-lab\n")
	if _, err := cli.Write(msg); err != nil {
		os.Exit(1)
	}
	buf := make([]byte, len(msg))
	if _, err := io.ReadFull(srv, buf); err != nil {
		os.Exit(1)
	}
}
