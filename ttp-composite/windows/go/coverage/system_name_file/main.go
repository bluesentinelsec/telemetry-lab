//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Println("COMPOSITE_CASE system_name_file")
	if !fixture.Begin("system_name_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, "C:\\lab\\windows-coverage\\work\\svchost.exe")
	fixture.Success("system_name_file")
}
