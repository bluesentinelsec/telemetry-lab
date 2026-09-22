//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE office_startup_file\n")
	if !fixture.Begin("office_startup_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\document.rtf`, fixture.AppData(`Microsoft\Word\STARTUP\telemetry-lab-fixture.rtf`))
	fixture.Success("office_startup_file")
}
