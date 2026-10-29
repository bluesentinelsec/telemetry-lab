// Target rule: Suspicious File Created In PerfLogs
// Sigma rule ID: 8822f47b-fcbf-b189-f9a1-10961c8f7cd0
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_perflogs_susp_files.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE perflogs_file\n")
	if !fixture.Begin("perflogs_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\PerfLogs\\telemetry-lab\\fixture.exe")
	fixture.Success("perflogs_file")
}
