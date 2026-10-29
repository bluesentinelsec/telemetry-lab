// Target rule: Uncommon Connection to Active Directory Web Services
// Sigma rule ID: ae8c1c58-4743-c0c8-3b30-7d69f7cbee68
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_adws_unusual_connection.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE tcp_connect_9389\n")
	if !fixture.Begin("tcp_connect_9389") {
		fixture.Hold()
		return
	}
	netio.Exchange("9389")
	fixture.Hold()
	fixture.Success("tcp_connect_9389")
}
