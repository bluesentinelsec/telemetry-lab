// Target rule: Path To Screensaver Binary Modified
// Sigma rule ID: ec1e8c56-2fa0-7417-e4b3-517d291e30b2
// Ruleset path: sigma/sysmon/registry/registry_event/registry_event_modify_screensaver_binary_path.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_screensaver\n")
	if !fixture.Begin("registry_screensaver") {
		return
	}
	regops.SetRegistry(`Control Panel\Desktop`, `SCRNSAVE.EXE`, `C:\lab\windows-coverage\fixtures\helper.exe`)
	fixture.Success("registry_screensaver")
}
