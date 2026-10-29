// Target rule: Search Private Keys or Passwords
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("search_private_keys") {
		return
	}
	cmd := exec.Command("/usr/bin/grep", "BEGIN PRIVATE", "/tmp/lab/key-search")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "BEGIN PRIVATE KEY telemetry-lab\n", "utility output")
	fmt.Printf("CASE_OK search_private_keys\n")
}
