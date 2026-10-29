// Target rule: Write below etc
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("etc_write") {
		return
	}
	files.Write("/etc/lab_fixture")
	fmt.Print("CASE_OK etc_write\n")
}
