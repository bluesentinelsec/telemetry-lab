// Target rule: New Custom Shim Database Created
// Sigma rule ID: 4211e288-60d6-2bb1-01c3-b7b3191126a9
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_new_shim_database.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE shim_database_file\n")
	if !fixture.Begin("shim_database_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, "C:\\Windows\\AppPatch\\Custom\\telemetry-lab-fixture.sdb")
	fixture.Success("shim_database_file")
}
