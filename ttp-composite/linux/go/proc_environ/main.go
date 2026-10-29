// Target rule: Read environment variable from /proc files
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"bytes"
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("proc_environ") {
		return
	}
	data, err := os.ReadFile("/proc/self/environ")
	fixture.Must(err)
	fixture.Check(bytes.Contains(data, []byte("TELEMETRY_LAB_FIXTURE=1")), "fixture environment")
	fmt.Print("CASE_OK proc_environ\n")
}
