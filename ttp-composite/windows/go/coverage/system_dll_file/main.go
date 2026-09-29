//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE system_dll_file\n")
	if !fixture.Begin("system_dll_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\fixture.node`, "C:\\lab\\windows-coverage\\work\\secur32.dll")
	fixture.Success("system_dll_file")
}
