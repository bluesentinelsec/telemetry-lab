//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE powershell_profile\n")
	if !fixture.Begin("powershell_profile") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\profile.ps1`, fixture.AppData(`Microsoft\Windows\PowerShell\Microsoft.PowerShell_profile.ps1`))
	fixture.Success("powershell_profile")
}
