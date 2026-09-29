//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE shim_database_file\n")
	if !fixture.Begin("shim_database_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, "C:\\Windows\\AppPatch\\Custom\\telemetry-lab-fixture.sdb")
	fixture.Success("shim_database_file")
}
