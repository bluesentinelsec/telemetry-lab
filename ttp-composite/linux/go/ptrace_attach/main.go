// Target rule: PTRACE attached to process
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/process"
)

func main() {
	if !fixture.Begin("ptrace_attach") {
		return
	}
	process.Attach()
	fmt.Print("CASE_OK ptrace_attach\n")
}
