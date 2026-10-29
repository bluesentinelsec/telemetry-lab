// Target rule: Displaying Hidden Files Feature Disabled
// Sigma rule ID: 96cd46a9-33dc-28dc-273e-83bc1fd8adc9
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_hide_file.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_hide_files\n")
	if !fixture.Begin("registry_hide_files") {
		return
	}
	regops.SetDword("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden", 0)
	fixture.Success("registry_hide_files")
}
