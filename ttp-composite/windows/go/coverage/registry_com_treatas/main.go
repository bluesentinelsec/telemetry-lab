//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Println("COMPOSITE_CASE registry_com_treatas")
	if !fixture.Begin("registry_com_treatas") {
		return
	}
	regops.SetRegistry("Software\\Classes\\CLSID\\{9B9C8026-806D-41E2-992A-909553D7A52A}\\TreatAs", "", "{9B9C8026-806D-41E2-992A-909553D7A52A}")
	fixture.Success("registry_com_treatas")
}
