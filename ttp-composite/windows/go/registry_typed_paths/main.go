// Target rule: Potential Persistence Via TypedPaths
// Sigma rule ID: a1229092-bf43-58f9-b9b4-f8fc3da816e6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_typed_paths.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_typed_paths\n")
	if !fixture.Begin("registry_typed_paths") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths", "url99", "C:\\lab\\windows-coverage\\work")
	fixture.Success("registry_typed_paths")
}
