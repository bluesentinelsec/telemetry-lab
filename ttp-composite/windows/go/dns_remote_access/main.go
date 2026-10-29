// Target rule: DNS Query To Remote Access Software Domain From Non-Browser App
// Sigma rule ID: d064cacb-bfe5-9d2b-7e5d-a8346829a158
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_remote_access_software_domains_non_browsers.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
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
