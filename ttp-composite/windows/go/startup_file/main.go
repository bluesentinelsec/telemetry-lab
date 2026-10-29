// Target rule: Startup Folder File Write
// Sigma rule ID: daaf04a9-5b60-e331-6611-a3a32797e550
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_startup_folder_file_write.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE startup_file\n")
	if !fixture.Begin("startup_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, fixture.AppData(`Microsoft\Windows\Start Menu\Programs\Startup\telemetry-lab-fixture.txt`))
	fixture.Success("startup_file")
}
