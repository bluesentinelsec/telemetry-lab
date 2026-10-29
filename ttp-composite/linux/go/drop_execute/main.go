// Target rule: Drop and execute new binary in container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/process"
)

func main() {
	if !fixture.Begin("drop_execute") {
		return
	}
	process.ExecuteHelper("/tmp/lab-helper", false)
	fmt.Print("CASE_OK drop_execute\n")
}
