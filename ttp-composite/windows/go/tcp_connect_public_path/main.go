// Target rule: Network Connection Initiated From Process Located In Potentially Suspicious Or Uncommon Location
// Sigma rule ID: df13f270-859b-272a-9c2a-a0ef744a0480
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_initiated_uncommon_or_suspicious_locations.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/netio"
	"os"
	"strings"
)

func main() {
	fmt.Print("COMPOSITE_CASE tcp_connect_public_path\n")
	if !fixture.Begin("tcp_connect_public_path") {
		fixture.Hold()
		return
	}
	image, err := os.Executable()
	fixture.Must(err)
	fixture.Check(strings.EqualFold(image, `C:\Users\Public\telemetry-lab\probe.exe`), "wrong executable path")
	netio.Exchange("49152")
	fixture.Hold()
	fixture.Success("tcp_connect_public_path")
}
