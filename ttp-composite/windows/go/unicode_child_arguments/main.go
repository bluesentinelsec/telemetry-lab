// Target rule: Potential CommandLine Obfuscation Using Unicode Characters
// Sigma rule ID: efe8a84a-0bef-c646-b13a-5a3cbe2b01b9
// Ruleset path: sigma/sysmon/threat-hunting/process_creation/proc_creation_win_susp_cli_obfuscation_unicode.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"os/exec"
)

func main() {
	fmt.Print("COMPOSITE_CASE unicode_child_arguments\n")
	if !fixture.Begin("unicode_child_arguments") {
		return
	}
	cmd := exec.Command(fixture.Root+`\fixtures\helper.exe`, "marker\u00a0value")
	output, err := cmd.CombinedOutput()
	fmt.Print(string(output))
	exit, ok := err.(*exec.ExitError)
	fixture.Check(ok && exit.ExitCode() == 43, "Unicode helper did not confirm exact argument")
	fixture.Success("unicode_child_arguments")
}
