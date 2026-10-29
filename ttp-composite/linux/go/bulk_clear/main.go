// Target rule: Remove Bulk Data from Disk
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os"
	"os/exec"
)

func main() {
	if !fixture.Begin("bulk_clear") {
		return
	}
	cmd := exec.Command("/usr/bin/shred", "-n", "0", "-z", "-s", "64", "/tmp/lab/shred-target")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "", "utility output")
	got, err := os.ReadFile("/tmp/lab/shred-target")
	fixture.Must(err)
	fixture.Check(string(got) == "\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000", "fixture bytes")
	fmt.Print("CASE_OK bulk_clear\n")
}
