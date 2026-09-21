package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("log_truncate") {
		return
	}
	files.Truncate("/var/log/lab.log")
	fmt.Print("CASE_OK log_truncate\n")
}
