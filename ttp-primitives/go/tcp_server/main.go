//go:build linux

package main

// tcp_server primitive: accept a TCP connection and receive data.
//
// The measured behaviour is the server path: listen -> accept -> read -> write
// reply. A loopback client on 127.0.0.1 and an ephemeral port drives the
// connection so the primitive is self-contained and offline. The exchange is
// single-threaded: the client connects into the listen backlog, then the server
// accepts, receives the request, and sends an echo reply which the client reads.
// The client is scaffolding; tcp_client is the primitive that emphasises it.
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

	req := []byte("telemetry-lab\n")
	if _, err := cli.Write(req); err != nil {
		os.Exit(1)
	}
	buf := make([]byte, len(req))
	if _, err := io.ReadFull(srv, buf); err != nil {
		os.Exit(1)
	}
	// echo reply back to the client
	if _, err := srv.Write(buf); err != nil {
		os.Exit(1)
	}
	reply := make([]byte, len(req))
	if _, err := io.ReadFull(cli, reply); err != nil {
		os.Exit(1)
	}
}
