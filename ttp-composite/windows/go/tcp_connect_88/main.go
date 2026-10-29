// Target rule: Uncommon Outbound Kerberos Connection
// Sigma rule ID: 322fd5f2-b5b7-1bf4-58f2-92873dc878bb
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_outbound_kerberos_connection.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
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
