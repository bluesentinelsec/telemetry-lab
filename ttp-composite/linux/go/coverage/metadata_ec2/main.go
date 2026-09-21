package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/network"
)

func main() {
	if !fixture.Begin("metadata_ec2") {
		return
	}
	network.Metadata()
	fmt.Print("CASE_OK metadata_ec2\n")
}
