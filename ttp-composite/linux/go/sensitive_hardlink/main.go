// Target rule: Create Hardlink Over Sensitive Files
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("sensitive_hardlink") {
		return
	}
	fixture.Must(os.Link("/etc/shadow", "/tmp/lab/hard"))
	a, err := os.Stat("/etc/shadow")
	fixture.Must(err)
	b, err := os.Stat("/tmp/lab/hard")
	fixture.Must(err)
	fixture.Check(os.SameFile(a, b), "same inode")
	fixture.Must(os.Remove("/tmp/lab/hard"))
	fmt.Print("CASE_OK sensitive_hardlink\n")
}
