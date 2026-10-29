// Target rule: Clear Log Activities
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("log_truncate") {
		return
	}
	files.Truncate("/var/log/lab.log")
	fmt.Print("CASE_OK log_truncate\n")
}
