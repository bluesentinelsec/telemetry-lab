// Target rule: Adding ssh keys to authorized_keys
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("authorized_keys") {
		return
	}
	files.Write("/root/.ssh/authorized_keys")
	fmt.Print("CASE_OK authorized_keys\n")
}
