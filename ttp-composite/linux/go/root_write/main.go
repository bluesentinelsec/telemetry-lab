// Target rule: Write below root
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("root_write") {
		return
	}
	files.Write("/root/lab_fixture")
	fmt.Print("CASE_OK root_write\n")
}
