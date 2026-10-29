// Target rule: Redirect STDOUT/STDIN to Network Connection in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/network"
)

func main() {
	if !fixture.Begin("reverse_shell") {
		return
	}
	network.ReverseShell()
	fmt.Print("CASE_OK reverse_shell\n")
}
