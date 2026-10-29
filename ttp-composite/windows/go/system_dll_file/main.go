// Target rule: Files With System DLL Name In Unsuspected Locations
// Sigma rule ID: 47b821bf-c853-813b-eaa2-be2620f42a1d
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_system_dll_files.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE system_dll_file\n")
	if !fixture.Begin("system_dll_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\fixture.node`, "C:\\lab\\windows-coverage\\work\\secur32.dll")
	fixture.Success("system_dll_file")
}
