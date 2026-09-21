package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("ssh_read") {
		return
	}
	files.Read("/root/.ssh/lab_key")
	fmt.Print("CASE_OK ssh_read\n")
}
