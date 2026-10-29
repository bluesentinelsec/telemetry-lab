// Target rule: Read Shell Configuration File
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("shell_config_read") {
		return
	}
	b, e := os.ReadFile("/root/.bashrc")
	fixture.Must(e)
	fixture.Check(string(b) == fixture.Payload, "bytes")
	fmt.Print("CASE_OK shell_config_read\n")
}
