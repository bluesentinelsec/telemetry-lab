//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE tcp_connect_88\n")
	if !fixture.Begin("tcp_connect_88") {
		fixture.Hold()
		return
	}
	netio.Exchange("88")
	fixture.Hold()
	fixture.Success("tcp_connect_88")
}
