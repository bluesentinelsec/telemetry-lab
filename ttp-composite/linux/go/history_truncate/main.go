// Target rule: Delete or rename shell history
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("history_truncate") {
		return
	}
	files.Truncate("/root/.bash_history")
	fmt.Print("CASE_OK history_truncate\n")
}
