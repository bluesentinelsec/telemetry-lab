package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("setid_mode") {
		return
	}
	files.Write("/tmp/lab/mode")
	fixture.Must(os.Chmod("/tmp/lab/mode", 0600|os.ModeSetuid))
	st, err := os.Stat("/tmp/lab/mode")
	fixture.Must(err)
	fixture.Check(st.Mode()&os.ModeSetuid != 0, "setuid mode")
	fmt.Print("CASE_OK setid_mode\n")
}
