package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("repository_write") {
		return
	}
	files.Write("/etc/apt/sources.list.d/lab.list")
	fmt.Print("CASE_OK repository_write\n")
}
