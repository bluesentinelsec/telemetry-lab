// Target rule: Potential File Extension Spoofing Using Right-to-Left Override
// Sigma rule ID: 1522de8d-352b-1bb8-509b-932d2dd4bb60
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_right_to_left_override_extension_spoofing.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE rtlo_file\n")
	if !fixture.Begin("rtlo_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\lab\\windows-coverage\\work\\report‮fdp.exe")
	fixture.Success("rtlo_file")
}
