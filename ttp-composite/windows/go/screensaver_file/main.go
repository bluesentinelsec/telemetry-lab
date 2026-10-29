// Target rule: Suspicious Screensaver Binary File Creation
// Sigma rule ID: b7a6c875-41bf-5648-744f-d236cceb1c26
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_scr_binary_file.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE screensaver_file\n")
	if !fixture.Begin("screensaver_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\lab\\windows-coverage\\work\\fixture.scr")
	fixture.Success("screensaver_file")
}
