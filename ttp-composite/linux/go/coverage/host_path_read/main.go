package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("host_path_read") {
		return
	}
	files.Read("/host/telemetry-lab/fixture")
	fmt.Printf("CASE_OK host_path_read\n")
}
