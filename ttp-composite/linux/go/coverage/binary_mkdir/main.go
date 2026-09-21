package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("binary_mkdir") {
		return
	}
	fixture.Must(os.Mkdir("/usr/bin/lab_directory", 0700))
	st, err := os.Stat("/usr/bin/lab_directory")
	fixture.Must(err)
	fixture.Check(st.IsDir(), "directory created")
	fixture.Must(os.Remove("/usr/bin/lab_directory"))
	fmt.Print("CASE_OK binary_mkdir\n")
}
