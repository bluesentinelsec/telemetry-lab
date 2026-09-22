//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_active_setup\n")
	if !fixture.Begin("registry_active_setup") {
		return
	}
	regops.SetRegistry(`Software\Microsoft\Active Setup\Installed Components\{9B9C8026-806D-41E2-992A-909553D7A52A}`, `StubPath`, `C:\lab\windows-coverage\fixtures\helper.exe`)
	fixture.Success("registry_active_setup")
}
