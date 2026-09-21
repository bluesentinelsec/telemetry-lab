package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/network"
)

func main() {
	if !fixture.Begin("udp_exchange") {
		return
	}
	network.UDP()
	fmt.Print("CASE_OK udp_exchange\n")
}
