package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
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
