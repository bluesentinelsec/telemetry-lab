//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Println("COMPOSITE_CASE rtlo_file")
	if !fixture.Begin("rtlo_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\lab\\windows-coverage\\work\\report‮fdp.exe")
	fixture.Success("rtlo_file")
}
