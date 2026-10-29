// Target rule: COM Hijacking via TreatAs
// Sigma rule ID: 6655602f-690f-f834-4dd4-c12213d0c687
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_treatas_persistence.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_com_treatas\n")
	if !fixture.Begin("registry_com_treatas") {
		return
	}
	regops.SetRegistry("Software\\Classes\\CLSID\\{9B9C8026-806D-41E2-992A-909553D7A52A}\\TreatAs", "", "{9B9C8026-806D-41E2-992A-909553D7A52A}")
	fixture.Success("registry_com_treatas")
}
