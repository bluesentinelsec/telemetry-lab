// Target rule: PowerShell Console History Logs Deleted
// Sigma rule ID: 14680f1d-0b5e-e92c-0ea0-dcd01321c0e8
// Ruleset path: sigma/sysmon/file/file_delete/file_delete_win_delete_powershell_command_history.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"os"
)

func main() {
	fmt.Printf("COMPOSITE_CASE delete_history_fixture\n")
	if !fixture.Begin("delete_history_fixture") {
		return
	}
	path := "C:\\lab\\windows-coverage\\work\\PSReadLine\\ConsoleHost_history.txt"
	fixture.Must(os.Remove(path))
	_, err := os.Stat(path)
	fixture.Check(os.IsNotExist(err), "fixture still exists")
	fixture.Success("delete_history_fixture")
}
