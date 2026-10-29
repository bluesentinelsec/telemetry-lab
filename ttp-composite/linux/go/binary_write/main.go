// Target rule: Write below binary dir
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("binary_write") {
		return
	}
	files.Write("/usr/bin/lab_fixture")
	fmt.Print("CASE_OK binary_write\n")
}
