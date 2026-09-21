package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("cron_write") {
		return
	}
	files.Write("/etc/cron.d/lab_fixture")
	fmt.Print("CASE_OK cron_write\n")
}
