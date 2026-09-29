//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
)

func main() {
	fmt.Print("COMPOSITE_CASE dns_ldap_discovery\n")
	if !fixture.Begin("dns_ldap_discovery") {
		return
	}
	netio.Resolve("_ldap.telemetry-lab.test")
	fixture.Success("dns_ldap_discovery")
}
