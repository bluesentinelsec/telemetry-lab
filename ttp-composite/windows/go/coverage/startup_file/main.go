//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE startup_file\n")
	if !fixture.Begin("startup_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, fixture.AppData(`Microsoft\Windows\Start Menu\Programs\Startup\telemetry-lab-fixture.txt`))
	fixture.Success("startup_file")
}
