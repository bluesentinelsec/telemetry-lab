// Target rule: Potential Local Privilege Escalation via Environment Variables Misuse
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os"
	"os/exec"
)

func main() {
	if !fixture.Begin("glibc_tunable_child") {
		return
	}
	cmd := exec.Command("/opt/coverage/helper")
	cmd.Env = append(os.Environ(), "GLIBC_TUNABLES=glibc.malloc.trim_threshold=131072")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "HELPER_OK\n", "utility output")
	fmt.Printf("CASE_OK glibc_tunable_child\n")
}
