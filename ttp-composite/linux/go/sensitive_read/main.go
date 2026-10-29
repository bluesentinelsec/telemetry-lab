// Target rule: Read sensitive file untrusted
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("sensitive_read") {
		return
	}
	files.Read("/etc/shadow")
	fmt.Print("CASE_OK sensitive_read\n")
}
