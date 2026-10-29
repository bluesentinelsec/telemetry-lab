// Target rule: DNS Query To Common Malware Hosting and Shortener Services
// Sigma rule ID: 7909c849-d650-4178-8739-9884f75c17fe
// Ruleset path: sigma/sysmon/dns_query/dns_query_win_common_malware_hosting_services.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
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
