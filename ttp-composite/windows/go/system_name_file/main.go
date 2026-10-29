// Target rule: Files With System Process Name In Unsuspected Locations
// Sigma rule ID: eccfe194-f618-b054-3986-7f7529f079f1
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_system_file.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE system_name_file\n")
	if !fixture.Begin("system_name_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\lab\\windows-coverage\\work\\svchost.exe")
	fixture.Success("system_name_file")
}
