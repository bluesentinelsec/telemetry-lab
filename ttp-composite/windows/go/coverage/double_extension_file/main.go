//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE double_extension_file\n")
	if !fixture.Begin("double_extension_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, `C:\lab\windows-coverage\work\report.pdf.exe`)
	fixture.Success("double_extension_file")
}
