// Target rule: Suspicious Binaries and Scripts in Public Folder
// Sigma rule ID: ef4c38c9-e26f-dcfe-1cbe-6323bafb8f39
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_public_folder_extension.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE public_binary\n")
	if !fixture.Begin("public_binary") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, `C:\Users\Public\telemetry-lab\fixture.exe`)
	fixture.Success("public_binary")
}
