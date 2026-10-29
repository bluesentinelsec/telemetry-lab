// Target rule: Directory traversal monitored file read
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("traversal_read") {
		return
	}
	files.Read("/tmp/lab/../../etc/shadow")
	fmt.Print("CASE_OK traversal_read\n")
}
