// Target rule: Potential Persistence Via Microsoft Office Startup Folder
// Sigma rule ID: be512a1b-170e-acff-f35d-0e4b44caa2a3
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_office_startup_persistence.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE office_startup_file\n")
	if !fixture.Begin("office_startup_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\document.rtf`, fixture.AppData(`Microsoft\Word\STARTUP\telemetry-lab-fixture.rtf`))
	fixture.Success("office_startup_file")
}
