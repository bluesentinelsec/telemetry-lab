// Target rule: Execution from /dev/shm
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/process"
)

func main() {
	if !fixture.Begin("exec_shm") {
		return
	}
	process.ExecuteHelper("/dev/shm/lab-helper", false)
	fmt.Print("CASE_OK exec_shm\n")
}
