// Target rule: Potential Persistence Using DebugPath
// Sigma rule ID: 1fa31aa7-117f-4356-a2ab-7062be19c8a6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_appx_debugger.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_appx_debugger\n")
	if !fixture.Begin("registry_appx_debugger") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Windows\\CurrentVersion\\PackagedAppXDebug\\Microsoft.TelemetryLabFixture", "", "C:\\lab\\windows-coverage\\fixtures\\helper.exe")
	fixture.Success("registry_appx_debugger")
}
