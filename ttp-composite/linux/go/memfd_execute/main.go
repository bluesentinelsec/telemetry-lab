// Target rule: Fileless execution via memfd_create
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/process"
)

func main() {
	if !fixture.Begin("memfd_execute") {
		return
	}
	process.ExecuteHelper("", true)
	fmt.Print("CASE_OK memfd_execute\n")
}
