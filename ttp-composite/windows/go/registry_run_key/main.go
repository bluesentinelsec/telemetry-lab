// Target rule: CurrentVersion Autorun Keys Modification
// Sigma rule ID: 3f59aeed-e4fb-6b21-a7fa-a327fdb8494d
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_asep_reg_keys_modification_currentversion.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_run_key\n")
	if !fixture.Begin("registry_run_key") {
		return
	}
	regops.SetRegistry(`Software\Microsoft\Windows\CurrentVersion\Run`, `TelemetryLabCoverage`, `C:\lab\windows-coverage\fixtures\helper.exe`)
	fixture.Success("registry_run_key")
}
