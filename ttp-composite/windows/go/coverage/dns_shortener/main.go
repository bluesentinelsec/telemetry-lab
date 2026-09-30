//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE dns_shortener\n")
	if !fixture.Begin("dns_shortener") {
		fixture.Hold()
		return
	}
	netio.Resolve("tinyurl.com")
	fixture.Hold()
	fixture.Success("dns_shortener")
}
