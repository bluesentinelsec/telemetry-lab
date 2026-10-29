// Target rule: Decoding Payload in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("decode_base64") {
		return
	}
	cmd := exec.Command("/usr/bin/base64", "--decode", "/tmp/lab/encoded")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
	fmt.Printf("CASE_OK decode_base64\n")
}
