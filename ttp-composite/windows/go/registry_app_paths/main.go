// Target rule: Potential Persistence Via App Paths Default Property
// Sigma rule ID: 140df4ae-d66c-c984-2165-595d754d0424
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_app_paths.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_app_paths\n")
	if !fixture.Begin("registry_app_paths") {
		return
	}
	regops.SetRegistry(`Software\Microsoft\Windows\CurrentVersion\App Paths\telemetry-lab-fixture.exe`, ``, `C:\Users\Public\telemetry-lab\helper.exe`)
	fixture.Success("registry_app_paths")
}
