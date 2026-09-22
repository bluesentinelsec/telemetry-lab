//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_screensaver\n")
	if !fixture.Begin("registry_screensaver") {
		return
	}
	regops.SetRegistry(`Control Panel\Desktop`, `SCRNSAVE.EXE`, `C:\lab\windows-coverage\fixtures\helper.exe`)
	fixture.Success("registry_screensaver")
}
