//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE perflogs_file\n")
	if !fixture.Begin("perflogs_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\PerfLogs\\telemetry-lab\\fixture.exe")
	fixture.Success("perflogs_file")
}
