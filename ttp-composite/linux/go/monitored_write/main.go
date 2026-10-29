// Target rule: Write below monitored dir
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("monitored_write") {
		return
	}
	files.Write("/boot/lab_fixture")
	fmt.Print("CASE_OK monitored_write\n")
}
