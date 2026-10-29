// Target rule: Suspicious LNK Double Extension File Created
// Sigma rule ID: 6b7cbf57-a67c-6e5a-61c6-4d92d02fff3e
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_lnk_double_extension.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE double_extension_lnk\n")
	if !fixture.Begin("double_extension_lnk") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\fixture.lnk`, `C:\lab\windows-coverage\work\report.pdf.lnk`)
	fixture.Success("double_extension_lnk")
}
