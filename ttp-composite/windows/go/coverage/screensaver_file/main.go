//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Println("COMPOSITE_CASE screensaver_file")
	if !fixture.Begin("screensaver_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\lab\\windows-coverage\\work\\fixture.scr")
	fixture.Success("screensaver_file")
}
