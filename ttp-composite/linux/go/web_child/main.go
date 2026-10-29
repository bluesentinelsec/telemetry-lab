// Target rule: Web Server Spawned Suspicious Child Process
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("web_child") {
		return
	}
	cmd := exec.Command("/usr/bin/curl", "-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
	fmt.Print("CASE_OK web_child\n")
}
