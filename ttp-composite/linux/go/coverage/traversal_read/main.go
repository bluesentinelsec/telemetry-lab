package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("traversal_read") {
		return
	}
	files.Read("/tmp/lab/../../etc/shadow")
	fmt.Print("CASE_OK traversal_read\n")
}
