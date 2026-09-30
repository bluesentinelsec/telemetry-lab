//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE dns_remote_access\n")
	if !fixture.Begin("dns_remote_access") {
		fixture.Hold()
		return
	}
	netio.Resolve("api.splashtop.com")
	fixture.Hold()
	fixture.Success("dns_remote_access")
}
