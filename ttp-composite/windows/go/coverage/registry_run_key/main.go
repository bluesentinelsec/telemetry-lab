//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_run_key\n")
	if !fixture.Begin("registry_run_key") {
		return
	}
	regops.SetRegistry(`Software\Microsoft\Windows\CurrentVersion\Run`, `TelemetryLabCoverage`, `C:\lab\windows-coverage\fixtures\helper.exe`)
	fixture.Success("registry_run_key")
}
