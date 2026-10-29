// Target rule: Suspicious Double Extension Files
// Sigma rule ID: c69c8c8d-4188-72ea-ca61-a2a1a80612b3
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_double_extension.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE double_extension_file\n")
	if !fixture.Begin("double_extension_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, `C:\lab\windows-coverage\work\report.pdf.exe`)
	fixture.Success("double_extension_file")
}
