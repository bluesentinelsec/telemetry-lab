// Target rule: Potential Persistence Via Visual Studio Tools for Office
// Sigma rule ID: ee69bf67-79f6-5973-f69d-7a6f609c97db
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_office_vsto.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_word_addin\n")
	if !fixture.Begin("registry_word_addin") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Office\\Word\\Addins\\TelemetryLabFixture", "Manifest", "C:\\lab\\windows-coverage\\fixtures\\fixture.vsto")
	fixture.Success("registry_word_addin")
}
