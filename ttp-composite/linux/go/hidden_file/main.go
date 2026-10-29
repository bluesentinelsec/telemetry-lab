// Target rule: Create Hidden Files or Directories
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("hidden_file") {
		return
	}
	fixture.Must(os.WriteFile("/tmp/lab/.hidden-fixture", []byte(fixture.Payload), 0600))
	b, e := os.ReadFile("/tmp/lab/.hidden-fixture")
	fixture.Must(e)
	fixture.Check(string(b) == fixture.Payload, "bytes")
	fmt.Print("CASE_OK hidden_file\n")
}
