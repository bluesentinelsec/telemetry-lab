//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE tcp_connect_2525\n")
	if !fixture.Begin("tcp_connect_2525") {
		fixture.Hold()
		return
	}
	netio.Exchange("2525")
	fixture.Hold()
	fixture.Success("tcp_connect_2525")
}
