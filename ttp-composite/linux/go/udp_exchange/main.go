// Target rule: Unexpected UDP Traffic
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/network"
)

func main() {
	if !fixture.Begin("udp_exchange") {
		return
	}
	network.UDP()
	fmt.Print("CASE_OK udp_exchange\n")
}
