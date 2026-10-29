// Target rule: System procs network activity
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("shell_network") {
		return
	}
	cmd := exec.Command("/bin/bash", "-c", "exec 3<>/dev/tcp/198.18.0.1/4445; cat <&3")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
	fmt.Print("CASE_OK shell_network\n")
}
