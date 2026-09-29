//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Println("COMPOSITE_CASE registry_suspicious_env")
	if !fixture.Begin("registry_suspicious_env") {
		return
	}
	regops.SetRegistry("Environment", "TelemetryLabFixture", "C:\\Users\\Public\\telemetry-lab\\fixture.exe")
	fixture.Success("registry_suspicious_env")
}
