package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("sensitive_read") {
		return
	}
	files.Read("/etc/shadow")
	fmt.Print("CASE_OK sensitive_read\n")
}
