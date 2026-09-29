package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("release_agent_write") {
		return
	}
	files.Write("/tmp/lab/release_agent")
	fmt.Printf("CASE_OK release_agent_write\n")
}
