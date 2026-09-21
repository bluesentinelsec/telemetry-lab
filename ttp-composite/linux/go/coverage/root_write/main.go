package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("root_write") {
		return
	}
	files.Write("/root/lab_fixture")
	fmt.Print("CASE_OK root_write\n")
}
