//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE dns_ip_lookup\n")
	if !fixture.Begin("dns_ip_lookup") {
		return
	}
	netio.Resolve("api.ipify.org")
	fixture.Success("dns_ip_lookup")
}
