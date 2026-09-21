package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("history_truncate") {
		return
	}
	files.Truncate("/root/.bash_history")
	fmt.Print("CASE_OK history_truncate\n")
}
