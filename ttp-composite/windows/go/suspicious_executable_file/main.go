// Target rule: Suspicious Executable File Creation
// Sigma rule ID: 9512176f-0e9f-7f30-fa82-d414c1c80248
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_executable_creation.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE suspicious_executable_file\n")
	if !fixture.Begin("suspicious_executable_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, `C:\lab\windows-coverage\work\lab.sys.exe`)
	fixture.Success("suspicious_executable_file")
}
