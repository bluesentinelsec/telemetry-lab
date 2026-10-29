// Target rule: Suspicious Environment Variable Has Been Registered
// Sigma rule ID: eca534f8-005d-bb79-798d-0af4e2bf38d6
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_suspicious_env_variables.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_suspicious_env\n")
	if !fixture.Begin("registry_suspicious_env") {
		return
	}
	regops.SetRegistry("Environment", "TelemetryLabFixture", "C:\\Users\\Public\\telemetry-lab\\fixture.exe")
	fixture.Success("registry_suspicious_env")
}
