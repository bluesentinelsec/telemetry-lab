// Target rule: Suspicious DNS Query for IP Lookup Service APIs
// Sigma rule ID: e1d5e512-66be-e3eb-e24b-a9f3545e115a
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_susp_external_ip_lookup.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE dns_ip_lookup\n")
	if !fixture.Begin("dns_ip_lookup") {
		fixture.Hold()
		return
	}
	netio.Resolve("api.ipify.org")
	fixture.Hold()
	fixture.Success("dns_ip_lookup")
}
