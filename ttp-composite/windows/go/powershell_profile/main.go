// Target rule: PowerShell Profile Modification
// Sigma rule ID: 5d1e6a6b-91ca-c7e8-821c-5c665ad9ca5e
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_powershell_profile.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE powershell_profile\n")
	if !fixture.Begin("powershell_profile") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\profile.ps1`, fixture.AppData(`Microsoft\Windows\PowerShell\Microsoft.PowerShell_profile.ps1`))
	fixture.Success("powershell_profile")
}
