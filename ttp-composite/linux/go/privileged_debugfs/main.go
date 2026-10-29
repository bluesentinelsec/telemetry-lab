// Target rule: Debugfs Launched in Privileged Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("privileged_debugfs") {
		return
	}
	cmd := exec.Command("/usr/sbin/debugfs", "-R", "cat /marker", "/tmp/lab/filesystem.img")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
	fmt.Print("CASE_OK privileged_debugfs\n")
}
