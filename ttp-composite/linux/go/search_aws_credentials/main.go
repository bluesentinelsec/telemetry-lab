// Target rule: Find AWS Credentials
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("search_aws_credentials") {
		return
	}
	cmd := exec.Command("/usr/bin/grep", "aws_access_key_id", "/tmp/lab/aws-search")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "aws_access_key_id=telemetry-lab\n", "utility output")
	fmt.Printf("CASE_OK search_aws_credentials\n")
}
