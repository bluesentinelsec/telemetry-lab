// Target rule: Office Macros Warning Disabled
// Sigma rule ID: 8b6b4194-cfe8-b585-475f-5997e8015fe0
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_office_vba_warnings_tamper.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_office_macro\n")
	if !fixture.Begin("registry_office_macro") {
		return
	}
	regops.SetDword("Software\\Microsoft\\Office\\16.0\\Word\\Security", "VBAWarnings", 1)
	fixture.Success("registry_office_macro")
}
