// Target rule: Cloudflared Tunnels Related DNS Requests
// Sigma rule ID: a19966bd-8f14-3aaf-c121-4c5d016441d3
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_cloudflared_communication.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
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
