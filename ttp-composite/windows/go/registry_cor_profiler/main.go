// Target rule: Enabling COR Profiler Environment Variables
// Sigma rule ID: aeac22f7-e219-1561-df1f-f531ac2d096f
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_enabling_cor_profiler_env_variables.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_cor_profiler\n")
	if !fixture.Begin("registry_cor_profiler") {
		return
	}
	regops.SetRegistry("Environment", "COR_PROFILER", "{9B9C8026-806D-41E2-992A-909553D7A52A}")
	fixture.Success("registry_cor_profiler")
}
