//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE tcp_connect_3389\n")
	if !fixture.Begin("tcp_connect_3389") {
		fixture.Hold()
		return
	}
	conn := netio.Connect("3389")
	netio.SendAll(conn, []byte{3, 0, 0, 11, 6, 0xe0, 0, 0, 0, 0, 0})
	fixture.Must(conn.Close())
	fixture.Hold()
	fixture.Success("tcp_connect_3389")
}
