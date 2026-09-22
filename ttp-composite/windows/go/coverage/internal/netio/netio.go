//go:build windows

package netio

import (
	"bytes"
	"context"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"io"
	"net"
	"time"
)

func Connect(port string) net.Conn {
	conn, err := net.DialTimeout("tcp4", net.JoinHostPort("127.0.0.1", port), 5*time.Second)
	fixture.Must(err)
	fixture.Must(conn.SetDeadline(time.Now().Add(5 * time.Second)))
	return conn
}
func SendAll(conn net.Conn, payload []byte) {
	for len(payload) > 0 {
		n, err := conn.Write(payload)
		fixture.Must(err)
		fixture.Check(n > 0, "zero-byte socket write")
		payload = payload[n:]
	}
}
func Exchange(port string) {
	conn := Connect(port)
	payload := []byte("telemetry-lab\n")
	SendAll(conn, payload)
	reply := make([]byte, len(payload))
	_, err := io.ReadFull(conn, reply)
	fixture.Must(err)
	fixture.Check(bytes.Equal(payload, reply), "echo bytes differ")
	fixture.Must(conn.Close())
}
func Resolve(name string) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	answers, err := net.DefaultResolver.LookupIP(ctx, "ip4", name)
	fixture.Must(err)
	fixture.Check(len(answers) > 0, "no resolver answers")
	for _, ip := range answers {
		fixture.Check(ip.Equal(net.IPv4(127, 0, 0, 42)), "unexpected DNS answer")
	}
}
