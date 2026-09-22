//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE ads_executable\n")
	if !fixture.Begin("ads_executable") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, `C:\lab\windows-coverage\work\carrier.txt:fixture.exe`)
	fixture.Success("ads_executable")
}
