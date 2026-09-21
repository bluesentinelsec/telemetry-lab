package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("binary_rename") {
		return
	}
	fixture.Must(os.Rename("/usr/bin/lab_old", "/usr/bin/lab_new"))
	_, err := os.Stat("/usr/bin/lab_old")
	fixture.Check(os.IsNotExist(err), "old path removed")
	files.Read("/usr/bin/lab_new")
	fmt.Print("CASE_OK binary_rename\n")
}
