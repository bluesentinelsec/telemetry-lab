package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("rpm_database_write") {
		return
	}
	files.Write("/var/lib/rpm/telemetry-lab-fixture")
	fmt.Println("CASE_OK rpm_database_write")
}
