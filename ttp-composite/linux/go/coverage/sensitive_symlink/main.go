package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("sensitive_symlink") {
		return
	}
	fixture.Must(os.Symlink("/etc/shadow", "/tmp/lab/link"))
	target, err := os.Readlink("/tmp/lab/link")
	fixture.Must(err)
	fixture.Check(target == "/etc/shadow", "symlink target")
	fixture.Must(os.Remove("/tmp/lab/link"))
	fmt.Print("CASE_OK sensitive_symlink\n")
}
