// Target rule: Read ssh information
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("ssh_read") {
		return
	}
	files.Read("/root/.ssh/lab_key")
	fmt.Print("CASE_OK ssh_read\n")
}
