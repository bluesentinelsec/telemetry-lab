// Target rule: Update Package Repository
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("repository_write") {
		return
	}
	files.Write("/etc/apt/sources.list.d/lab.list")
	fmt.Print("CASE_OK repository_write\n")
}
