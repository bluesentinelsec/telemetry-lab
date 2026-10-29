// Target rule: Network Tool Executed During NPM Package Install
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("npm_network_tool") {
		return
	}
	cmd := exec.Command("/usr/bin/ncat", "--recv-only", "198.18.0.1", "4445")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
	fmt.Print("CASE_OK npm_network_tool\n")
}
