// Target rule: PowerShell Module File Created By Non-PowerShell Process
// Sigma rule ID: 103362bb-15b7-3bed-7f8c-fd7a15fe31f4
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_powershell_module_uncommon_creation.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"os"
	"path/filepath"
)

func main() {
	fmt.Printf("COMPOSITE_CASE powershell_module_file\n")
	if !fixture.Begin("powershell_module_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, filepath.Join(os.Getenv("USERPROFILE"), "Documents\\WindowsPowerShell\\Modules\\TelemetryLabFixture\\TelemetryLabFixture.psm1"))
	fixture.Success("powershell_module_file")
}
