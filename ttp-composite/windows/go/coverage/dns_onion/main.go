//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE dns_onion\n")
	if !fixture.Begin("dns_onion") {
		return
	}
	netio.Resolve("lab.onion")
	fixture.Success("dns_onion")
}
