//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE dns_cloudflared\n")
	if !fixture.Begin("dns_cloudflared") {
		fixture.Hold()
		return
	}
	netio.Resolve("protocol-v2.argotunnel.com")
	fixture.Hold()
	fixture.Success("dns_cloudflared")
}
