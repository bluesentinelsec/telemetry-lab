//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Println("COMPOSITE_CASE registry_word_addin")
	if !fixture.Begin("registry_word_addin") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Office\\Word\\Addins\\TelemetryLabFixture", "Manifest", "C:\\lab\\windows-coverage\\fixtures\\fixture.vsto")
	fixture.Success("registry_word_addin")
}
