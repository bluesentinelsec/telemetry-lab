// Target rule: Rclone Config File Creation
// Sigma rule ID: 1446e210-e8da-42a9-e7bf-8fb30a60366b
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_rclone_config_files.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE rclone_config_file\n")
	if !fixture.Begin("rclone_config_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, "C:\\Users\\Public\\.config\\rclone\\telemetry-lab-fixture.conf")
	fixture.Success("rclone_config_file")
}
