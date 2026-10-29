// Target rule: Contact cloud metadata service from container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/network"
)

func main() {
	if !fixture.Begin("metadata_cloud") {
		return
	}
	network.Metadata()
	fmt.Print("CASE_OK metadata_cloud\n")
}
