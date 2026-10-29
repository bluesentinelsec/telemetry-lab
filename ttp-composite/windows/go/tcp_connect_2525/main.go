// Target rule: Suspicious Outbound SMTP Connections
// Sigma rule ID: f8a59cdc-b3d1-8f59-c3f4-4db6d94e8efc
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_outbound_smtp_connections.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
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
