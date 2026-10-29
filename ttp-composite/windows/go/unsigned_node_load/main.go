// Target rule: Unsigned .node File Loaded
// Sigma rule ID: 8085fb71-ed3b-7920-ca06-f9174665cc8a
// Ruleset path: sigma/sysmon/image_load/image_load_dll_unsigned_node_load.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"golang.org/x/sys/windows"
)

func main() {
	fmt.Print("COMPOSITE_CASE unsigned_node_load\n")
	if !fixture.Begin("unsigned_node_load") {
		return
	}

	module, err := windows.LoadDLL(fixture.Root + `\fixtures\fixture.node`)
	fixture.Must(err)
	answer, err := module.FindProc("fixture_answer")
	fixture.Must(err)
	result, _, _ := answer.Call()
	fixture.Check(result == 42, "module answer differs")
	fixture.Must(module.Release())

	fixture.Success("unsigned_node_load")
}
