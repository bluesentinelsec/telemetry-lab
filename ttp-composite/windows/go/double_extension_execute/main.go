// Target rule: Suspicious Double Extension File Execution
// Sigma rule ID: b6ce0b2f-593b-5e1c-e137-d30b2974e30e
// Ruleset path: sigma/sysmon/process_creation/proc_creation_win_susp_double_extension.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"os/exec"
)

func main() {
	fmt.Print("COMPOSITE_CASE double_extension_execute\n")
	if !fixture.Begin("double_extension_execute") {
		return
	}

	command := exec.Command(fixture.Root + `\work\report.pdf.exe`)
	err := command.Run()
	fixture.Check(err != nil && command.ProcessState != nil && command.ProcessState.ExitCode() == 42, "helper did not return 42")

	fixture.Success("double_extension_execute")
}
