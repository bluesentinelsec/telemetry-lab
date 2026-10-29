// Target rule: Modify Shell Configuration File
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("shell_config_write") {
		return
	}
	files.Write("/root/.bashrc")
	fmt.Print("CASE_OK shell_config_write\n")
}
