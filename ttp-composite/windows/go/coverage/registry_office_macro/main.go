//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_office_macro\n")
	if !fixture.Begin("registry_office_macro") {
		return
	}
	regops.SetDword("Software\\Microsoft\\Office\\16.0\\Word\\Security", "VBAWarnings", 1)
	fixture.Success("registry_office_macro")
}
