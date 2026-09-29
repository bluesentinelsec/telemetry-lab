//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Println("COMPOSITE_CASE registry_appx_debugger")
	if !fixture.Begin("registry_appx_debugger") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Windows\\CurrentVersion\\PackagedAppXDebug\\Microsoft.TelemetryLabFixture", "", "C:\\lab\\windows-coverage\\fixtures\\helper.exe")
	fixture.Success("registry_appx_debugger")
}
