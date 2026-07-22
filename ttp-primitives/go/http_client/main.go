//go:build linux

package main

// http_client primitive: perform HTTP GET and POST requests.
//
// HTTP is the most common application-layer channel for staging and C2. The
// request/response is hand-rolled over a raw TCP conn -- deliberately NOT
// net/http -- so the primitive adds no HTTP-stack machinery and mirrors the C
// raw-socket decision (see issue #43 for why the TLS https_client is deferred).
// It stays self-contained and offline by talking to a loopback responder on
// 127.0.0.1 and an ephemeral port, single-threaded via the listen backlog. Both
// a GET and a POST are issued to exercise both methods.
//
// At the syscall level this is the tcp_client path plus HTTP framing in the
// payload; the point is the request/response round-trip, not a full HTTP client.
// The cgo/static substrate split lives in anchor_cgo.go.
// Linux-only for this pass (Winsock on Windows -- issue #44).

import (
	"io"
	"net"
	"os"
)

// exchange runs one full HTTP round-trip over loopback: client dials and sends
// `request`, the server accepts and reads it and replies, the client reads the
// reply. Both ends stay open throughout the exchange (matching the C ordering in
// ttp-primitives/c/http_client/main.c), so no send races a closed peer.
func exchange(ln net.Listener, request string) bool {
	cli, err := net.Dial("tcp", ln.Addr().String())
	if err != nil {
		return false
	}
	defer cli.Close()

	srv, err := ln.Accept()
	if err != nil {
		return false
	}
	defer srv.Close()

	if _, err := cli.Write([]byte(request)); err != nil {
		return false
	}

	buf := make([]byte, 512)
	if _, err := srv.Read(buf); err != nil { // server reads the request
		return false
	}

	resp := "HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok"
	if _, err := srv.Write([]byte(resp)); err != nil {
		return false
	}

	if _, err := cli.Read(buf); err != nil && err != io.EOF { // client reads the response
		return false
	}
	return true
}

func main() {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		os.Exit(1)
	}
	defer ln.Close()

	get := "GET / HTTP/1.0\r\nHost: localhost\r\n\r\n"
	post := "POST / HTTP/1.0\r\nHost: localhost\r\n" +
		"Content-Length: 14\r\n\r\ntelemetry-lab\n"

	if !exchange(ln, get) {
		os.Exit(1)
	}
	if !exchange(ln, post) {
		os.Exit(1)
	}
}
