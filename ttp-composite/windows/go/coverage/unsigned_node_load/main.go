//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
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
