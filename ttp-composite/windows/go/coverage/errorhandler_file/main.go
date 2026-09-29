//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE errorhandler_file\n")
	if !fixture.Begin("errorhandler_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, "C:\\Windows\\Setup\\Scripts\\ErrorHandler.cmd")
	fixture.Success("errorhandler_file")
}
