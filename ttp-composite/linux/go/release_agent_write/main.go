// Target rule: Detect release_agent File Container Escapes
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("release_agent_write") {
		return
	}
	files.Write("/tmp/lab/release_agent")
	fmt.Printf("CASE_OK release_agent_write\n")
}
