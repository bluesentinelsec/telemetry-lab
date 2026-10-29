// Target rule: Create files below dev
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("dev_file") {
		return
	}
	files.Write("/dev/lab_fixture")
	fmt.Print("CASE_OK dev_file\n")
}
